use std::path::Path;

use pb_scan::{scan_directories, scan_directory};

fn fixtures_dir() -> &'static Path {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("fixtures")
        .leak()
}

#[test]
fn test_simple_python() {
    let result = scan_directory(&fixtures_dir().join("simple-python"));

    // Languages
    let lang_names: Vec<&str> = result.languages.iter().map(|l| l.name.as_str()).collect();
    assert!(
        lang_names.contains(&"Python"),
        "expected Python in {lang_names:?}"
    );

    // Frameworks (from requirements.txt)
    let fw_names: Vec<&str> = result.frameworks.iter().map(|f| f.name.as_str()).collect();
    assert!(
        fw_names.contains(&"Flask"),
        "expected Flask in {fw_names:?}"
    );
    assert!(
        fw_names.contains(&"Requests"),
        "expected Requests in {fw_names:?}"
    );
    assert!(
        fw_names.contains(&"pytest"),
        "expected pytest in {fw_names:?}"
    );
    assert!(
        fw_names.contains(&"Python Package"),
        "expected Python Package in {fw_names:?}"
    );

    // Infrastructure (Dockerfile)
    let infra_names: Vec<&str> = result
        .infrastructure_signals
        .iter()
        .map(|s| s.name.as_str())
        .collect();
    assert!(
        infra_names.contains(&"Docker"),
        "expected Docker in {infra_names:?}"
    );

    // Structure
    assert!(
        result
            .project_structures
            .contains(&"python_package".to_string()),
        "expected python_package in {:?}",
        result.project_structures
    );
}

#[test]
fn test_node_react() {
    let result = scan_directory(&fixtures_dir().join("node-react"));

    // Languages
    let lang_names: Vec<&str> = result.languages.iter().map(|l| l.name.as_str()).collect();
    assert!(
        lang_names.contains(&"TypeScript"),
        "expected TypeScript in {lang_names:?}"
    );

    // Frameworks (from package.json)
    let fw_names: Vec<&str> = result.frameworks.iter().map(|f| f.name.as_str()).collect();
    assert!(
        fw_names.contains(&"React"),
        "expected React in {fw_names:?}"
    );
    assert!(fw_names.contains(&"Vite"), "expected Vite in {fw_names:?}");
    assert!(
        fw_names.contains(&"TypeScript"),
        "expected TypeScript in {fw_names:?}"
    );

    // Structure
    assert!(result
        .project_structures
        .contains(&"node_project".to_string()));
    assert!(result
        .project_structures
        .contains(&"src_layout".to_string()));
}

#[test]
fn test_rust_actix() {
    let result = scan_directory(&fixtures_dir().join("rust-actix"));

    // Languages
    let lang_names: Vec<&str> = result.languages.iter().map(|l| l.name.as_str()).collect();
    assert!(
        lang_names.contains(&"Rust"),
        "expected Rust in {lang_names:?}"
    );

    // Frameworks (from Cargo.toml)
    let fw_names: Vec<&str> = result.frameworks.iter().map(|f| f.name.as_str()).collect();
    assert!(
        fw_names.contains(&"Actix Web"),
        "expected Actix Web in {fw_names:?}"
    );
    assert!(
        fw_names.contains(&"Tokio"),
        "expected Tokio in {fw_names:?}"
    );
    assert!(
        fw_names.contains(&"Serde"),
        "expected Serde in {fw_names:?}"
    );

    // Structure
    assert!(result
        .project_structures
        .contains(&"src_layout".to_string()));
}

#[test]
fn test_monorepo() {
    let result = scan_directory(&fixtures_dir().join("monorepo"));

    // Infrastructure
    let infra_names: Vec<&str> = result
        .infrastructure_signals
        .iter()
        .map(|s| s.name.as_str())
        .collect();
    assert!(
        infra_names.contains(&"Docker Compose"),
        "expected Docker Compose in {infra_names:?}"
    );
    assert!(
        infra_names.contains(&"GitHub Actions"),
        "expected GitHub Actions in {infra_names:?}"
    );

    // Structure
    assert!(result.project_structures.contains(&"monorepo".to_string()));
}

#[test]
fn test_multi_directory_scan() {
    let fixtures = fixtures_dir();
    let result = scan_directories(&[
        &fixtures.join("simple-python"),
        &fixtures.join("node-react"),
    ]);

    // Should have languages from both
    let lang_names: Vec<&str> = result.languages.iter().map(|l| l.name.as_str()).collect();
    assert!(lang_names.contains(&"Python"));
    assert!(lang_names.contains(&"TypeScript"));

    // Percentages should sum to ~100
    let total: f64 = result.languages.iter().map(|l| l.percentage).sum();
    assert!(
        (total - 100.0).abs() < 1.0,
        "percentages should sum to ~100, got {total}"
    );

    // Should have frameworks from both
    let fw_names: Vec<&str> = result.frameworks.iter().map(|f| f.name.as_str()).collect();
    assert!(fw_names.contains(&"Flask"));
    assert!(fw_names.contains(&"React"));

    // Should have structures from both
    assert!(result
        .project_structures
        .contains(&"python_package".to_string()));
    assert!(result
        .project_structures
        .contains(&"node_project".to_string()));
}

#[test]
fn test_json_output_shape() {
    let result = scan_directory(&fixtures_dir().join("simple-python"));
    let json = serde_json::to_value(&result).unwrap();

    assert!(json["languages"].is_array());
    assert!(json["frameworks"].is_array());
    assert!(json["project_structures"].is_array());
    assert!(json["infrastructure_signals"].is_array());

    // Check language entry shape
    let first_lang = &json["languages"][0];
    assert!(first_lang["name"].is_string());
    assert!(first_lang["category"].is_string());
    assert!(first_lang["percentage"].is_f64());
    assert_eq!(first_lang["category"], "language");

    // Check framework entry shape
    if let Some(first_fw) = json["frameworks"].as_array().and_then(|a| a.first()) {
        assert!(first_fw["name"].is_string());
        assert!(first_fw["category"].is_string());
    }
}
