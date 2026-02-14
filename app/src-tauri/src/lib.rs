use std::process::Command;

/// Resolve the `projectbridge` CLI binary path.
/// Checks `PROJECTBRIDGE_BIN` env var first, then falls back to PATH lookup.
fn pb_binary() -> String {
    std::env::var("PROJECTBRIDGE_BIN").unwrap_or_else(|_| "projectbridge".to_string())
}

#[tauri::command]
fn run_analysis(args: Vec<String>) -> Result<String, String> {
    let output = Command::new(pb_binary())
        .args(&args)
        .output()
        .map_err(|e| format!("Failed to run projectbridge: {}", e))?;

    if output.status.success() {
        String::from_utf8(output.stdout)
            .map_err(|e| format!("Invalid UTF-8 output: {}", e))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("projectbridge failed: {}", stderr))
    }
}

#[tauri::command]
fn run_analysis_form(
    github_user: String,
    job_text: String,
    resume_text: Option<String>,
    no_ai: bool,
) -> Result<String, String> {
    let mut cmd_args = vec![
        "analyze".to_string(),
        "--github-user".to_string(),
        github_user,
        "--job-text".to_string(),
        job_text,
    ];

    if let Some(resume) = resume_text {
        if !resume.is_empty() {
            cmd_args.push("--resume-text".to_string());
            cmd_args.push(resume);
        }
    }

    if no_ai {
        cmd_args.push("--no-ai".to_string());
    }

    run_analysis(cmd_args)
}

#[tauri::command]
fn export_analysis(analysis_json: String, format: String) -> Result<String, String> {
    let tmp = std::env::temp_dir().join("pb_export_input.json");
    std::fs::write(&tmp, &analysis_json)
        .map_err(|e| format!("Failed to write temp file: {}", e))?;

    let output = Command::new(pb_binary())
        .args(["export", "--input", tmp.to_str().unwrap(), "--format", &format])
        .output()
        .map_err(|e| format!("Failed to run projectbridge: {}", e))?;

    let _ = std::fs::remove_file(&tmp);

    if output.status.success() {
        String::from_utf8(output.stdout)
            .map_err(|e| format!("Invalid UTF-8 output: {}", e))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("projectbridge export failed: {}", stderr))
    }
}

#[tauri::command]
fn scan_local_repos(paths: Vec<String>) -> Result<String, String> {
    let mut cmd_args = vec!["analyze".to_string(), "--no-ai".to_string()];
    cmd_args.push("--local-repos".to_string());
    cmd_args.extend(paths);
    // Use a placeholder job text for local-only scans.
    cmd_args.push("--job-text".to_string());
    cmd_args.push("Local repository scan".to_string());

    run_analysis(cmd_args)
}

#[tauri::command]
fn export_project_spec(
    analysis_json: String,
    recommendation_index: usize,
    difficulty: String,
    format: Option<String>,
    no_ai: bool,
) -> Result<String, String> {
    let tmp = std::env::temp_dir().join("pb_export_project_input.json");
    std::fs::write(&tmp, &analysis_json)
        .map_err(|e| format!("Failed to write temp file: {}", e))?;

    let fmt = format.unwrap_or_else(|| "markdown".to_string());

    let mut cmd_args = vec![
        "export-project".to_string(),
        "--input".to_string(),
        tmp.to_str().unwrap().to_string(),
        "--recommendation".to_string(),
        recommendation_index.to_string(),
        "--difficulty".to_string(),
        difficulty,
        "--format".to_string(),
        fmt,
    ];

    if no_ai {
        cmd_args.push("--no-ai".to_string());
    }

    let output = Command::new(pb_binary())
        .args(&cmd_args)
        .output()
        .map_err(|e| format!("Failed to run projectbridge: {}", e))?;

    let _ = std::fs::remove_file(&tmp);

    if output.status.success() {
        String::from_utf8(output.stdout)
            .map_err(|e| format!("Invalid UTF-8 output: {}", e))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("projectbridge export-project failed: {}", stderr))
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            run_analysis,
            run_analysis_form,
            export_analysis,
            scan_local_repos,
            export_project_spec
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
