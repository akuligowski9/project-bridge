use std::collections::HashMap;
use std::path::Path;

use crate::output::LanguageEntry;

/// Map file extensions to language names.
pub fn extension_to_language(ext: &str) -> Option<&'static str> {
    match ext {
        "py" => Some("Python"),
        "js" => Some("JavaScript"),
        "jsx" => Some("JavaScript"),
        "ts" => Some("TypeScript"),
        "tsx" => Some("TypeScript"),
        "rs" => Some("Rust"),
        "go" => Some("Go"),
        "rb" => Some("Ruby"),
        "java" => Some("Java"),
        "kt" => Some("Kotlin"),
        "swift" => Some("Swift"),
        "c" => Some("C"),
        "h" => Some("C"),
        "cpp" | "cc" | "cxx" => Some("C++"),
        "hpp" => Some("C++"),
        "cs" => Some("C#"),
        "php" => Some("PHP"),
        "scala" => Some("Scala"),
        "r" | "R" => Some("R"),
        "dart" => Some("Dart"),
        "lua" => Some("Lua"),
        "ex" | "exs" => Some("Elixir"),
        "erl" | "hrl" => Some("Erlang"),
        "hs" => Some("Haskell"),
        "ml" | "mli" => Some("OCaml"),
        "clj" | "cljs" => Some("Clojure"),
        "jl" => Some("Julia"),
        "zig" => Some("Zig"),
        "svelte" => Some("Svelte"),
        "vue" => Some("Vue"),
        "html" | "htm" => Some("HTML"),
        "css" => Some("CSS"),
        "scss" | "sass" => Some("SCSS"),
        "less" => Some("Less"),
        "sql" => Some("SQL"),
        "sh" | "bash" | "zsh" => Some("Shell"),
        "ps1" => Some("PowerShell"),
        _ => None,
    }
}

/// Returns true for binary file extensions that should be skipped.
pub fn is_binary_extension(ext: &str) -> bool {
    matches!(
        ext,
        "png"
            | "jpg"
            | "jpeg"
            | "gif"
            | "bmp"
            | "ico"
            | "svg"
            | "webp"
            | "woff"
            | "woff2"
            | "ttf"
            | "eot"
            | "otf"
            | "mp3"
            | "mp4"
            | "wav"
            | "avi"
            | "mov"
            | "mkv"
            | "zip"
            | "tar"
            | "gz"
            | "bz2"
            | "xz"
            | "7z"
            | "rar"
            | "exe"
            | "dll"
            | "so"
            | "dylib"
            | "a"
            | "o"
            | "obj"
            | "wasm"
            | "pyc"
            | "pyo"
            | "class"
            | "pdf"
            | "doc"
            | "docx"
            | "xls"
            | "xlsx"
            | "db"
            | "sqlite"
            | "sqlite3"
    )
}

/// Accumulate bytes per language from a file path and its metadata size.
pub fn record_language(path: &Path, size: u64, bytes_by_lang: &mut HashMap<String, u64>) {
    if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
        if let Some(lang) = extension_to_language(ext) {
            *bytes_by_lang.entry(lang.to_string()).or_insert(0) += size;
        }
    }
}

/// Convert accumulated byte counts into sorted `LanguageEntry` list.
pub fn build_language_list(bytes_by_lang: &HashMap<String, u64>) -> Vec<LanguageEntry> {
    let total: u64 = bytes_by_lang.values().sum();
    if total == 0 {
        return Vec::new();
    }
    let mut entries: Vec<LanguageEntry> = bytes_by_lang
        .iter()
        .map(|(name, &bytes)| LanguageEntry {
            name: name.clone(),
            category: "language".to_string(),
            percentage: ((bytes as f64 / total as f64) * 1000.0).round() / 10.0,
        })
        .collect();
    entries.sort_by(|a, b| b.percentage.partial_cmp(&a.percentage).unwrap());
    entries
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extension_mapping() {
        assert_eq!(extension_to_language("py"), Some("Python"));
        assert_eq!(extension_to_language("rs"), Some("Rust"));
        assert_eq!(extension_to_language("ts"), Some("TypeScript"));
        assert_eq!(extension_to_language("tsx"), Some("TypeScript"));
        assert_eq!(extension_to_language("svelte"), Some("Svelte"));
        assert_eq!(extension_to_language("unknown"), None);
    }

    #[test]
    fn test_binary_detection() {
        assert!(is_binary_extension("png"));
        assert!(is_binary_extension("wasm"));
        assert!(!is_binary_extension("py"));
        assert!(!is_binary_extension("rs"));
    }

    #[test]
    fn test_build_language_list() {
        let mut bytes = HashMap::new();
        bytes.insert("Python".to_string(), 700);
        bytes.insert("JavaScript".to_string(), 300);

        let list = build_language_list(&bytes);
        assert_eq!(list.len(), 2);
        assert_eq!(list[0].name, "Python");
        assert_eq!(list[0].percentage, 70.0);
        assert_eq!(list[1].name, "JavaScript");
        assert_eq!(list[1].percentage, 30.0);
    }

    #[test]
    fn test_build_language_list_empty() {
        let bytes = HashMap::new();
        let list = build_language_list(&bytes);
        assert!(list.is_empty());
    }
}
