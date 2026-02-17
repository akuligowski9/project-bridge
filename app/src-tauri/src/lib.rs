use std::io::{Read, Write};
use std::net::TcpStream;
use std::process::Command;
use std::time::Duration;

/// Resolve the `projectbridge` CLI binary path.
/// Checks `PROJECTBRIDGE_BIN` env var first, then falls back to PATH lookup.
fn pb_binary() -> String {
    std::env::var("PROJECTBRIDGE_BIN").unwrap_or_else(|_| "projectbridge".to_string())
}

/// Execute the `projectbridge` CLI with the given args and optional env vars.
fn execute_pb(args: Vec<String>, env_vars: Vec<(String, String)>) -> Result<String, String> {
    let mut cmd = Command::new(pb_binary());
    cmd.args(&args);
    for (key, val) in &env_vars {
        cmd.env(key, val);
    }

    let output = cmd
        .output()
        .map_err(|e| format!("Failed to run projectbridge: {}", e))?;

    if output.status.success() {
        String::from_utf8(output.stdout).map_err(|e| format!("Invalid UTF-8 output: {}", e))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("projectbridge failed: {}", stderr))
    }
}

#[tauri::command]
fn run_analysis(args: Vec<String>) -> Result<String, String> {
    execute_pb(args, vec![])
}

#[tauri::command]
fn run_analysis_form(
    github_user: String,
    job_text: String,
    resume_text: Option<String>,
    provider: String,
    api_key: Option<String>,
) -> Result<String, String> {
    let job_is_url = job_text.starts_with("http://") || job_text.starts_with("https://");
    let mut cmd_args = vec![
        "analyze".to_string(),
        "--github-user".to_string(),
        github_user,
        if job_is_url { "--job-url" } else { "--job-text" }.to_string(),
        job_text,
    ];

    if let Some(resume) = resume_text {
        if !resume.is_empty() {
            cmd_args.push("--resume-text".to_string());
            cmd_args.push(resume);
        }
    }

    cmd_args.push("--provider".to_string());
    cmd_args.push(provider.clone());

    let mut env_vars: Vec<(String, String)> = vec![];
    if let Some(key) = api_key {
        if !key.is_empty() {
            match provider.as_str() {
                "openai" => env_vars.push(("OPENAI_API_KEY".to_string(), key)),
                "anthropic" => env_vars.push(("ANTHROPIC_API_KEY".to_string(), key)),
                _ => {}
            }
        }
    }

    execute_pb(cmd_args, env_vars)
}

#[tauri::command]
fn export_analysis(analysis_json: String, format: String) -> Result<String, String> {
    let tmp = std::env::temp_dir().join("pb_export_input.json");
    std::fs::write(&tmp, &analysis_json)
        .map_err(|e| format!("Failed to write temp file: {}", e))?;

    let result = execute_pb(
        vec![
            "export".to_string(),
            "--input".to_string(),
            tmp.to_str().unwrap().to_string(),
            "--format".to_string(),
            format,
        ],
        vec![],
    );

    let _ = std::fs::remove_file(&tmp);
    result
}

#[tauri::command]
fn scan_local_repos(paths: Vec<String>) -> Result<String, String> {
    let mut cmd_args = vec!["analyze".to_string(), "--provider".to_string(), "none".to_string()];
    cmd_args.push("--local-repos".to_string());
    cmd_args.extend(paths);
    // Use a placeholder job text for local-only scans.
    cmd_args.push("--job-text".to_string());
    cmd_args.push("Local repository scan".to_string());

    execute_pb(cmd_args, vec![])
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

    let result = execute_pb(cmd_args, vec![]);

    let _ = std::fs::remove_file(&tmp);
    result
}

#[tauri::command]
fn list_ollama_models() -> Result<Vec<String>, String> {
    let mut stream = TcpStream::connect_timeout(
        &"127.0.0.1:11434".parse().unwrap(),
        Duration::from_secs(3),
    )
    .map_err(|_| "Ollama server is not reachable at localhost:11434".to_string())?;

    stream
        .set_read_timeout(Some(Duration::from_secs(5)))
        .map_err(|e| format!("Failed to set timeout: {}", e))?;

    let request = "GET /api/tags HTTP/1.0\r\nHost: localhost:11434\r\n\r\n";
    stream
        .write_all(request.as_bytes())
        .map_err(|e| format!("Failed to send request: {}", e))?;

    let mut response = String::new();
    stream
        .read_to_string(&mut response)
        .map_err(|e| format!("Failed to read response: {}", e))?;

    // Split HTTP headers from body.
    let body = response
        .split("\r\n\r\n")
        .nth(1)
        .ok_or_else(|| "Invalid HTTP response from Ollama".to_string())?;

    let parsed: serde_json::Value =
        serde_json::from_str(body).map_err(|e| format!("Invalid JSON from Ollama: {}", e))?;

    let models = parsed["models"]
        .as_array()
        .ok_or_else(|| "Unexpected response format from Ollama".to_string())?;

    let names: Vec<String> = models
        .iter()
        .filter_map(|m| m["name"].as_str().map(|s| s.to_string()))
        .collect();

    if names.is_empty() {
        return Err("No models found. Pull a model first: ollama pull llama3.2".to_string());
    }

    Ok(names)
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
            export_project_spec,
            list_ollama_models
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
