use std::collections::HashMap;
use std::path::Path;

use ignore::WalkBuilder;

use crate::dependencies;
use crate::frameworks::{detect_file_indicators, into_sorted_entries};
use crate::languages::{build_language_list, is_binary_extension, record_language};
use crate::output::ScanResult;
use crate::structures::detect_structures;

/// Directories to skip even without a .gitignore.
const SKIP_DIRS: &[&str] = &[
    "node_modules",
    "vendor",
    "__pycache__",
    "target",
    "build",
    "dist",
    ".git",
];

/// Hidden paths that are framework indicators — checked directly on disk
/// since the walker skips hidden files/dirs.
const HIDDEN_INDICATORS: &[&str] = &[
    ".github/workflows",
    ".gitlab-ci.yml",
    ".circleci",
    ".eslintrc.js",
    ".eslintrc.json",
    ".prettierrc",
    ".travis.yml",
];

/// Check for hidden-file indicators that the gitignore-aware walker skips.
fn check_hidden_indicators(root: &Path, top_level_names: &mut Vec<String>) {
    for &indicator in HIDDEN_INDICATORS {
        if root.join(indicator).exists() && !top_level_names.iter().any(|n| n == indicator) {
            top_level_names.push(indicator.to_string());
        }
    }
}

/// Scan a single directory and return aggregated results.
pub fn scan_directory(root: &Path) -> ScanResult {
    let mut bytes_by_lang: HashMap<String, u64> = HashMap::new();
    let mut top_level_names: Vec<String> = Vec::new();
    let mut frameworks: HashMap<String, String> = HashMap::new();
    let mut infra: HashMap<String, String> = HashMap::new();

    let walker = WalkBuilder::new(root)
        .hidden(true) // skip hidden files/dirs
        .git_ignore(true)
        .git_global(true)
        .git_exclude(true)
        .build();

    for entry in walker.flatten() {
        let path = entry.path();

        // Compute depth relative to root.
        let relative = match path.strip_prefix(root) {
            Ok(r) => r,
            Err(_) => continue,
        };

        // Skip the root itself.
        if relative.as_os_str().is_empty() {
            continue;
        }

        let depth = relative.components().count();

        // Record top-level entries (depth == 1).
        if depth == 1 {
            if let Some(name) = relative.file_name().and_then(|n| n.to_str()) {
                top_level_names.push(name.to_string());
            }
        }

        // Skip known junk directories.
        if entry.file_type().is_some_and(|ft| ft.is_dir()) {
            if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
                if SKIP_DIRS.contains(&name) {
                    continue;
                }
            }
            continue; // skip directories for language counting
        }

        // Skip binary files.
        if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
            if is_binary_extension(ext) {
                continue;
            }
        }

        // Count bytes per language.
        if let Ok(meta) = entry.metadata() {
            record_language(path, meta.len(), &mut bytes_by_lang);
        }
    }

    // Check for hidden indicators the walker skips (e.g. .github/workflows).
    check_hidden_indicators(root, &mut top_level_names);

    // Detect frameworks from file indicators.
    detect_file_indicators(&top_level_names, &mut frameworks, &mut infra);

    // Detect structures.
    let project_structures = detect_structures(&top_level_names);

    // Parse dependency files.
    dependencies::detect_all(root, &mut frameworks);

    ScanResult {
        languages: build_language_list(&bytes_by_lang),
        frameworks: into_sorted_entries(&frameworks),
        project_structures,
        infrastructure_signals: into_sorted_entries(&infra),
    }
}

/// Scan multiple directories and merge results.
pub fn scan_directories(roots: &[&Path]) -> ScanResult {
    let mut bytes_by_lang: HashMap<String, u64> = HashMap::new();
    let mut frameworks: HashMap<String, String> = HashMap::new();
    let mut infra: HashMap<String, String> = HashMap::new();
    let mut all_structures: std::collections::BTreeSet<String> = std::collections::BTreeSet::new();

    for root in roots {
        let result = scan_directory(root);

        // Merge languages by recombining byte counts isn't possible from percentages,
        // so we re-scan and merge at the byte level.
        // Actually, we need to re-do the walk for byte counts. Let's just merge the
        // individual scan results instead (frameworks/infra are deduped by HashMap).

        // For languages, we need the raw bytes. Let's just accumulate from each scan's
        // percentage-based output (approximation), or better: refactor to expose bytes.
        // Since we want exact merging, let's use a helper that returns raw bytes too.

        // For now, merge at the result level: treat each scan's percentages as weights.
        // This is an approximation. For proper merging we'd need byte counts.
        // Actually, let's just re-walk each directory for bytes directly.

        // Simpler approach: merge frameworks/infra/structures from individual results,
        // and for languages, do a combined walk.
        for entry in &result.frameworks {
            frameworks.insert(entry.name.clone(), entry.category.clone());
        }
        for entry in &result.infrastructure_signals {
            infra.insert(entry.name.clone(), entry.category.clone());
        }
        all_structures.extend(result.project_structures);
    }

    // Combined language walk across all roots.
    for root in roots {
        let walker = WalkBuilder::new(root)
            .hidden(true)
            .git_ignore(true)
            .git_global(true)
            .git_exclude(true)
            .build();

        for entry in walker.flatten() {
            let path = entry.path();
            if entry.file_type().is_some_and(|ft| ft.is_dir()) {
                continue;
            }
            if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                if is_binary_extension(ext) {
                    continue;
                }
            }
            if let Ok(meta) = entry.metadata() {
                record_language(path, meta.len(), &mut bytes_by_lang);
            }
        }
    }

    ScanResult {
        languages: build_language_list(&bytes_by_lang),
        frameworks: into_sorted_entries(&frameworks),
        project_structures: all_structures.into_iter().collect(),
        infrastructure_signals: into_sorted_entries(&infra),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_scan_empty_dir() {
        let tmp = TempDir::new().unwrap();
        let result = scan_directory(tmp.path());
        assert!(result.languages.is_empty());
        assert!(result.frameworks.is_empty());
        assert!(result.project_structures.is_empty());
        assert!(result.infrastructure_signals.is_empty());
    }

    #[test]
    fn test_scan_python_file() {
        let tmp = TempDir::new().unwrap();
        fs::write(tmp.path().join("main.py"), "print('hello')").unwrap();
        let result = scan_directory(tmp.path());
        assert_eq!(result.languages.len(), 1);
        assert_eq!(result.languages[0].name, "Python");
        assert_eq!(result.languages[0].percentage, 100.0);
    }

    #[test]
    fn test_scan_skips_binary() {
        let tmp = TempDir::new().unwrap();
        fs::write(tmp.path().join("main.py"), "print('hello')").unwrap();
        fs::write(tmp.path().join("image.png"), "fakepng").unwrap();
        let result = scan_directory(tmp.path());
        assert_eq!(result.languages.len(), 1);
        assert_eq!(result.languages[0].name, "Python");
    }

    #[test]
    fn test_scan_detects_structure() {
        let tmp = TempDir::new().unwrap();
        fs::create_dir(tmp.path().join("src")).unwrap();
        fs::write(tmp.path().join("Makefile"), "all:").unwrap();
        let result = scan_directory(tmp.path());
        assert!(result
            .project_structures
            .contains(&"src_layout".to_string()));
        assert!(result.project_structures.contains(&"makefile".to_string()));
    }

    #[test]
    fn test_scan_detects_infra() {
        let tmp = TempDir::new().unwrap();
        fs::write(tmp.path().join("Dockerfile"), "FROM python:3.12").unwrap();
        let result = scan_directory(tmp.path());
        assert!(result
            .infrastructure_signals
            .iter()
            .any(|s| s.name == "Docker"));
    }

    #[test]
    fn test_scan_multiple_dirs() {
        let tmp1 = TempDir::new().unwrap();
        let tmp2 = TempDir::new().unwrap();
        fs::write(tmp1.path().join("main.py"), "print('hello')").unwrap();
        fs::write(tmp2.path().join("app.rs"), "fn main() {}").unwrap();

        let result = scan_directories(&[tmp1.path(), tmp2.path()]);
        let lang_names: Vec<&str> = result.languages.iter().map(|l| l.name.as_str()).collect();
        assert!(lang_names.contains(&"Python"));
        assert!(lang_names.contains(&"Rust"));
    }
}
