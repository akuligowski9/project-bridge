/// Detect project structures from top-level directory/file names.
/// Direct port of GitHubAnalyzer._detect_structures() from github.py.
pub fn detect_structures(top_level_names: &[String]) -> Vec<String> {
    let mut structures: Vec<String> = Vec::new();
    let names: std::collections::HashSet<&str> =
        top_level_names.iter().map(|s| s.as_str()).collect();

    if names.contains("src") {
        structures.push("src_layout".to_string());
    }
    if names.contains("packages") || names.contains("libs") {
        structures.push("monorepo".to_string());
    }
    if names.contains("setup.py") || names.contains("pyproject.toml") {
        structures.push("python_package".to_string());
    }
    if names.contains("package.json") {
        structures.push("node_project".to_string());
    }
    if names.contains("Makefile") {
        structures.push("makefile".to_string());
    }

    structures.sort();
    structures
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_src_layout() {
        let names = vec!["src".to_string(), "README.md".to_string()];
        let result = detect_structures(&names);
        assert!(result.contains(&"src_layout".to_string()));
    }

    #[test]
    fn test_detect_monorepo() {
        let names = vec!["packages".to_string()];
        let result = detect_structures(&names);
        assert!(result.contains(&"monorepo".to_string()));
    }

    #[test]
    fn test_detect_python_package() {
        let names = vec!["pyproject.toml".to_string(), "src".to_string()];
        let result = detect_structures(&names);
        assert!(result.contains(&"python_package".to_string()));
        assert!(result.contains(&"src_layout".to_string()));
    }

    #[test]
    fn test_detect_node_project() {
        let names = vec!["package.json".to_string()];
        let result = detect_structures(&names);
        assert!(result.contains(&"node_project".to_string()));
    }

    #[test]
    fn test_detect_makefile() {
        let names = vec!["Makefile".to_string()];
        let result = detect_structures(&names);
        assert!(result.contains(&"makefile".to_string()));
    }

    #[test]
    fn test_detect_empty() {
        let names: Vec<String> = Vec::new();
        let result = detect_structures(&names);
        assert!(result.is_empty());
    }

    #[test]
    fn test_sorted_output() {
        let names = vec![
            "src".to_string(),
            "package.json".to_string(),
            "Makefile".to_string(),
        ];
        let result = detect_structures(&names);
        let mut sorted = result.clone();
        sorted.sort();
        assert_eq!(result, sorted);
    }
}
