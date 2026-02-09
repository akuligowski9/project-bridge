use std::process::Command;

#[tauri::command]
fn run_analysis(args: Vec<String>) -> Result<String, String> {
    let output = Command::new("projectbridge")
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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![run_analysis])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
