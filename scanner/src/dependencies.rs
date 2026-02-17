use std::collections::HashMap;
use std::fs;
use std::path::Path;

/// Detect frameworks from package.json dependencies.
/// Port of NPM_FRAMEWORK_MAP from github.py.
pub fn detect_npm(dir: &Path, frameworks: &mut HashMap<String, String>) {
    let path = dir.join("package.json");
    let content = match fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return,
    };
    let parsed: serde_json::Value = match serde_json::from_str(&content) {
        Ok(v) => v,
        Err(_) => return,
    };

    let mut all_deps: Vec<String> = Vec::new();
    for key in &["dependencies", "devDependencies"] {
        if let Some(obj) = parsed.get(key).and_then(|v| v.as_object()) {
            all_deps.extend(obj.keys().cloned());
        }
    }

    const NPM_MAP: &[(&str, &str, &str)] = &[
        ("react", "React", "framework"),
        ("react-native", "React Native", "framework"),
        ("next", "Next.js", "framework"),
        ("vue", "Vue", "framework"),
        ("nuxt", "Nuxt", "framework"),
        ("svelte", "Svelte", "framework"),
        ("@angular/core", "Angular", "framework"),
        ("express", "Express", "framework"),
        ("fastify", "Fastify", "framework"),
        ("gatsby", "Gatsby", "framework"),
        ("remix", "Remix", "framework"),
        ("@nestjs/core", "NestJS", "framework"),
        ("koa", "Koa", "framework"),
        ("tailwindcss", "Tailwind CSS", "framework"),
        ("prisma", "Prisma", "tool"),
        ("mongoose", "Mongoose", "tool"),
        ("sequelize", "Sequelize", "tool"),
        ("jest", "Jest", "tool"),
        ("mocha", "Mocha", "tool"),
        ("webpack", "Webpack", "tool"),
        ("vite", "Vite", "tool"),
        ("typescript", "TypeScript", "language"),
        ("three", "Three.js", "framework"),
        ("electron", "Electron", "framework"),
        ("socket.io", "Socket.IO", "framework"),
        ("graphql", "GraphQL", "tool"),
        ("@apollo/client", "Apollo", "framework"),
        ("redis", "Redis", "tool"),
        ("pg", "PostgreSQL", "tool"),
        ("mongodb", "MongoDB", "tool"),
        ("supabase", "Supabase", "tool"),
        ("firebase", "Firebase", "tool"),
    ];

    for &(dep, name, category) in NPM_MAP {
        if all_deps.iter().any(|d| d == dep) {
            frameworks.insert(name.to_string(), category.to_string());
        }
    }
}

/// Detect frameworks from requirements.txt.
/// Port of PYTHON_FRAMEWORK_MAP from github.py.
pub fn detect_python(dir: &Path, frameworks: &mut HashMap<String, String>) {
    let path = dir.join("requirements.txt");
    let content = match fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return,
    };
    let lower = content.to_lowercase();

    const PYTHON_MAP: &[(&str, &str, &str)] = &[
        ("django", "Django", "framework"),
        ("flask", "Flask", "framework"),
        ("fastapi", "FastAPI", "framework"),
        ("tornado", "Tornado", "framework"),
        ("celery", "Celery", "tool"),
        ("sqlalchemy", "SQLAlchemy", "tool"),
        ("pandas", "pandas", "framework"),
        ("numpy", "NumPy", "framework"),
        ("scipy", "SciPy", "framework"),
        ("scikit-learn", "scikit-learn", "framework"),
        ("tensorflow", "TensorFlow", "framework"),
        ("torch", "PyTorch", "framework"),
        ("pytest", "pytest", "tool"),
        ("pydantic", "Pydantic", "tool"),
        ("requests", "Requests", "tool"),
        ("boto3", "AWS SDK", "tool"),
        ("redis", "Redis", "tool"),
        ("psycopg2", "PostgreSQL", "tool"),
    ];

    for &(key, name, category) in PYTHON_MAP {
        if lower.contains(key) {
            frameworks.insert(name.to_string(), category.to_string());
        }
    }
}

/// Detect frameworks from Cargo.toml.
/// Port of RUST_CRATE_MAP from github.py.
pub fn detect_rust(dir: &Path, frameworks: &mut HashMap<String, String>) {
    let path = dir.join("Cargo.toml");
    let content = match fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return,
    };
    let lower = content.to_lowercase();

    const RUST_MAP: &[(&str, &str, &str)] = &[
        ("actix-web", "Actix Web", "framework"),
        ("axum", "Axum", "framework"),
        ("rocket", "Rocket", "framework"),
        ("tokio", "Tokio", "tool"),
        ("serde", "Serde", "tool"),
        ("diesel", "Diesel", "tool"),
        ("sqlx", "SQLx", "tool"),
        ("leptos", "Leptos", "framework"),
        ("yew", "Yew", "framework"),
        ("tauri", "Tauri", "framework"),
        ("wasm-bindgen", "WebAssembly", "tool"),
    ];

    for &(key, name, category) in RUST_MAP {
        if lower.contains(key) {
            frameworks.insert(name.to_string(), category.to_string());
        }
    }
}

/// Detect frameworks from Gemfile.
/// Port of RUBY_GEM_MAP from github.py.
pub fn detect_ruby(dir: &Path, frameworks: &mut HashMap<String, String>) {
    let path = dir.join("Gemfile");
    let content = match fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return,
    };
    let lower = content.to_lowercase();

    const RUBY_MAP: &[(&str, &str, &str)] = &[
        ("rails", "Ruby on Rails", "framework"),
        ("sinatra", "Sinatra", "framework"),
        ("sidekiq", "Sidekiq", "tool"),
        ("rspec", "RSpec", "tool"),
    ];

    for &(key, name, category) in RUBY_MAP {
        if lower.contains(key) {
            frameworks.insert(name.to_string(), category.to_string());
        }
    }
}

/// Detect frameworks from go.mod.
/// Port of GO_MODULE_MAP from github.py.
pub fn detect_go(dir: &Path, frameworks: &mut HashMap<String, String>) {
    let path = dir.join("go.mod");
    let content = match fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return,
    };

    const GO_MAP: &[(&str, &str, &str)] = &[
        ("github.com/gin-gonic/gin", "Gin", "framework"),
        ("github.com/gorilla/mux", "Gorilla Mux", "framework"),
        ("github.com/labstack/echo", "Echo", "framework"),
        ("github.com/gofiber/fiber", "Fiber", "framework"),
        ("gorm.io/gorm", "GORM", "tool"),
    ];

    for &(key, name, category) in GO_MAP {
        if content.contains(key) {
            frameworks.insert(name.to_string(), category.to_string());
        }
    }
}

/// Detect frameworks from composer.json.
/// Port of PHP_PACKAGE_MAP from github.py.
pub fn detect_php(dir: &Path, frameworks: &mut HashMap<String, String>) {
    let path = dir.join("composer.json");
    let content = match fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return,
    };
    let parsed: serde_json::Value = match serde_json::from_str(&content) {
        Ok(v) => v,
        Err(_) => return,
    };

    let mut all_deps: Vec<String> = Vec::new();
    for key in &["require", "require-dev"] {
        if let Some(obj) = parsed.get(key).and_then(|v| v.as_object()) {
            all_deps.extend(obj.keys().cloned());
        }
    }

    const PHP_MAP: &[(&str, &str, &str)] = &[
        ("laravel/framework", "Laravel", "framework"),
        ("symfony/symfony", "Symfony", "framework"),
        ("slim/slim", "Slim", "framework"),
    ];

    for &(dep, name, category) in PHP_MAP {
        if all_deps.iter().any(|d| d == dep) {
            frameworks.insert(name.to_string(), category.to_string());
        }
    }
}

/// Detect frameworks from pyproject.toml dependencies.
/// Fallback for Python projects that don't use requirements.txt.
pub fn detect_pyproject(dir: &Path, frameworks: &mut HashMap<String, String>) {
    let path = dir.join("pyproject.toml");
    let content = match fs::read_to_string(&path) {
        Ok(c) => c,
        Err(_) => return,
    };
    let lower = content.to_lowercase();

    const PYTHON_MAP: &[(&str, &str, &str)] = &[
        ("django", "Django", "framework"),
        ("flask", "Flask", "framework"),
        ("fastapi", "FastAPI", "framework"),
        ("tornado", "Tornado", "framework"),
        ("celery", "Celery", "tool"),
        ("sqlalchemy", "SQLAlchemy", "tool"),
        ("pandas", "pandas", "framework"),
        ("numpy", "NumPy", "framework"),
        ("scipy", "SciPy", "framework"),
        ("scikit-learn", "scikit-learn", "framework"),
        ("tensorflow", "TensorFlow", "framework"),
        ("torch", "PyTorch", "framework"),
        ("pytest", "pytest", "tool"),
        ("pydantic", "Pydantic", "tool"),
        ("requests", "Requests", "tool"),
        ("boto3", "AWS SDK", "tool"),
        ("redis", "Redis", "tool"),
        ("psycopg2", "PostgreSQL", "tool"),
    ];

    for &(key, name, category) in PYTHON_MAP {
        if lower.contains(key) {
            frameworks.insert(name.to_string(), category.to_string());
        }
    }
}

/// Run all dependency parsers for a given directory.
pub fn detect_all(dir: &Path, frameworks: &mut HashMap<String, String>) {
    detect_npm(dir, frameworks);
    detect_python(dir, frameworks);
    detect_pyproject(dir, frameworks);
    detect_rust(dir, frameworks);
    detect_ruby(dir, frameworks);
    detect_go(dir, frameworks);
    detect_php(dir, frameworks);
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_detect_npm_react() {
        let tmp = TempDir::new().unwrap();
        fs::write(
            tmp.path().join("package.json"),
            r#"{"dependencies": {"react": "^18.0.0", "express": "^4.0.0"}}"#,
        )
        .unwrap();
        let mut fw = HashMap::new();
        detect_npm(tmp.path(), &mut fw);
        assert!(fw.contains_key("React"));
        assert!(fw.contains_key("Express"));
    }

    #[test]
    fn test_detect_python_flask() {
        let tmp = TempDir::new().unwrap();
        fs::write(
            tmp.path().join("requirements.txt"),
            "flask==2.3.0\nrequests\n",
        )
        .unwrap();
        let mut fw = HashMap::new();
        detect_python(tmp.path(), &mut fw);
        assert!(fw.contains_key("Flask"));
        assert!(fw.contains_key("Requests"));
    }

    #[test]
    fn test_detect_rust_actix() {
        let tmp = TempDir::new().unwrap();
        fs::write(
            tmp.path().join("Cargo.toml"),
            "[dependencies]\nactix-web = \"4\"\ntokio = { version = \"1\" }\n",
        )
        .unwrap();
        let mut fw = HashMap::new();
        detect_rust(tmp.path(), &mut fw);
        assert!(fw.contains_key("Actix Web"));
        assert!(fw.contains_key("Tokio"));
    }

    #[test]
    fn test_detect_go_gin() {
        let tmp = TempDir::new().unwrap();
        fs::write(
            tmp.path().join("go.mod"),
            "module example.com/app\nrequire github.com/gin-gonic/gin v1.9.0\n",
        )
        .unwrap();
        let mut fw = HashMap::new();
        detect_go(tmp.path(), &mut fw);
        assert!(fw.contains_key("Gin"));
    }

    #[test]
    fn test_detect_missing_file() {
        let tmp = TempDir::new().unwrap();
        let mut fw = HashMap::new();
        detect_npm(tmp.path(), &mut fw);
        assert!(fw.is_empty());
    }

    #[test]
    fn test_detect_php_laravel() {
        let tmp = TempDir::new().unwrap();
        fs::write(
            tmp.path().join("composer.json"),
            r#"{"require": {"laravel/framework": "^10.0"}}"#,
        )
        .unwrap();
        let mut fw = HashMap::new();
        detect_php(tmp.path(), &mut fw);
        assert!(fw.contains_key("Laravel"));
    }

    #[test]
    fn test_detect_pyproject_flask() {
        let tmp = TempDir::new().unwrap();
        fs::write(
            tmp.path().join("pyproject.toml"),
            "[project]\ndependencies = [\n  \"flask>=2.3.0\",\n  \"pydantic>=2.0\",\n]\n",
        )
        .unwrap();
        let mut fw = HashMap::new();
        detect_pyproject(tmp.path(), &mut fw);
        assert!(fw.contains_key("Flask"));
        assert!(fw.contains_key("Pydantic"));
    }

    #[test]
    fn test_detect_ruby_rails() {
        let tmp = TempDir::new().unwrap();
        fs::write(
            tmp.path().join("Gemfile"),
            "source 'https://rubygems.org'\ngem 'rails', '~> 7.0'\ngem 'rspec'\n",
        )
        .unwrap();
        let mut fw = HashMap::new();
        detect_ruby(tmp.path(), &mut fw);
        assert!(fw.contains_key("Ruby on Rails"));
        assert!(fw.contains_key("RSpec"));
    }
}
