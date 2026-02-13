use std::collections::HashMap;

use crate::output::SignalEntry;

/// File/dir indicator → (name, category).
/// Direct port of FRAMEWORK_INDICATORS from github.py.
const FRAMEWORK_INDICATORS: &[(&str, &str, &str)] = &[
    // Infrastructure
    ("Dockerfile", "Docker", "infrastructure"),
    ("docker-compose.yml", "Docker Compose", "infrastructure"),
    ("docker-compose.yaml", "Docker Compose", "infrastructure"),
    (".github/workflows", "GitHub Actions", "infrastructure"),
    (".gitlab-ci.yml", "GitLab CI", "infrastructure"),
    (".circleci", "CircleCI", "infrastructure"),
    ("Jenkinsfile", "Jenkins", "infrastructure"),
    ("terraform", "Terraform", "infrastructure"),
    ("kubernetes", "Kubernetes", "infrastructure"),
    ("k8s", "Kubernetes", "infrastructure"),
    ("helm", "Helm", "infrastructure"),
    (".travis.yml", "Travis CI", "infrastructure"),
    ("netlify.toml", "Netlify", "infrastructure"),
    ("vercel.json", "Vercel", "infrastructure"),
    ("fly.toml", "Fly.io", "infrastructure"),
    ("render.yaml", "Render", "infrastructure"),
    ("nginx.conf", "Nginx", "infrastructure"),
    ("Vagrantfile", "Vagrant", "infrastructure"),
    ("ansible", "Ansible", "infrastructure"),
    // Tools
    (".eslintrc.js", "ESLint", "tool"),
    (".eslintrc.json", "ESLint", "tool"),
    ("tailwind.config.js", "Tailwind CSS", "framework"),
    ("tailwind.config.ts", "Tailwind CSS", "framework"),
    ("tsconfig.json", "TypeScript", "language"),
    ("webpack.config.js", "Webpack", "tool"),
    ("vite.config.ts", "Vite", "tool"),
    ("vite.config.js", "Vite", "tool"),
    (".prettierrc", "Prettier", "tool"),
    ("jest.config.js", "Jest", "tool"),
    ("jest.config.ts", "Jest", "tool"),
    ("pytest.ini", "pytest", "tool"),
    ("pyproject.toml", "Python Package", "tool"),
    ("Cargo.toml", "Rust", "language"),
    ("go.mod", "Go", "language"),
    ("Gemfile", "Ruby", "language"),
    ("composer.json", "PHP", "language"),
    ("build.gradle", "Gradle", "tool"),
    ("pom.xml", "Maven", "tool"),
];

/// Detect frameworks and infrastructure from top-level file/dir names.
pub fn detect_file_indicators(
    top_level_names: &[String],
    frameworks: &mut HashMap<String, String>,
    infra: &mut HashMap<String, String>,
) {
    for &(indicator, name, category) in FRAMEWORK_INDICATORS {
        if top_level_names.iter().any(|n| n == indicator) {
            if category == "infrastructure" {
                infra.insert(name.to_string(), category.to_string());
            } else {
                frameworks.insert(name.to_string(), category.to_string());
            }
        }
    }
}

/// Convert HashMap accumulators into sorted SignalEntry vectors.
pub fn into_sorted_entries(map: &HashMap<String, String>) -> Vec<SignalEntry> {
    let mut entries: Vec<SignalEntry> = map
        .iter()
        .map(|(name, category)| SignalEntry {
            name: name.clone(),
            category: category.clone(),
        })
        .collect();
    entries.sort();
    entries
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_dockerfile() {
        let names = vec!["Dockerfile".to_string(), "src".to_string()];
        let mut fw = HashMap::new();
        let mut infra = HashMap::new();
        detect_file_indicators(&names, &mut fw, &mut infra);
        assert!(infra.contains_key("Docker"));
        assert!(!fw.contains_key("Docker"));
    }

    #[test]
    fn test_detect_framework_indicator() {
        let names = vec!["tailwind.config.js".to_string()];
        let mut fw = HashMap::new();
        let mut infra = HashMap::new();
        detect_file_indicators(&names, &mut fw, &mut infra);
        assert!(fw.contains_key("Tailwind CSS"));
        assert_eq!(fw["Tailwind CSS"], "framework");
    }

    #[test]
    fn test_detect_language_indicator() {
        let names = vec!["tsconfig.json".to_string()];
        let mut fw = HashMap::new();
        let mut infra = HashMap::new();
        detect_file_indicators(&names, &mut fw, &mut infra);
        assert!(fw.contains_key("TypeScript"));
        assert_eq!(fw["TypeScript"], "language");
    }

    #[test]
    fn test_sorted_entries() {
        let mut map = HashMap::new();
        map.insert("Zebra".to_string(), "framework".to_string());
        map.insert("Alpha".to_string(), "tool".to_string());
        let entries = into_sorted_entries(&map);
        assert_eq!(entries[0].name, "Alpha");
        assert_eq!(entries[1].name, "Zebra");
    }
}
