use std::path::PathBuf;
use std::time::Instant;

use clap::Parser;

use pb_scan::{scan_directories, scan_directory};

#[derive(Parser)]
#[command(name = "pb-scan", about = "Scan local repositories for ProjectBridge")]
struct Cli {
    /// Directory to scan (default: current directory).
    #[arg(default_value = ".")]
    path: PathBuf,

    /// Scan multiple directories and merge results.
    #[arg(long, num_args = 1..)]
    paths: Option<Vec<PathBuf>>,

    /// Pretty-print JSON output.
    #[arg(long)]
    pretty: bool,

    /// Print scan stats to stderr.
    #[arg(long)]
    stats: bool,
}

// Workaround: clap doesn't natively support "if --paths is given, ignore positional".
// We handle it manually: if --paths is provided, use those; otherwise use the positional arg.

fn main() {
    let cli = Cli::parse();
    let start = Instant::now();

    let result = if let Some(ref dirs) = cli.paths {
        let paths: Vec<&std::path::Path> = dirs.iter().map(|p| p.as_path()).collect();

        // Validate all paths exist.
        for p in &paths {
            if !p.is_dir() {
                eprintln!("Error: not a directory: {}", p.display());
                std::process::exit(1);
            }
        }

        scan_directories(&paths)
    } else {
        if !cli.path.is_dir() {
            eprintln!("Error: not a directory: {}", cli.path.display());
            std::process::exit(1);
        }
        scan_directory(&cli.path)
    };

    let elapsed = start.elapsed();

    let json = if cli.pretty {
        serde_json::to_string_pretty(&result).expect("Failed to serialize result")
    } else {
        serde_json::to_string(&result).expect("Failed to serialize result")
    };

    println!("{json}");

    if cli.stats {
        eprintln!(
            "Scanned in {:.1}ms | {} languages | {} frameworks | {} infra signals",
            elapsed.as_secs_f64() * 1000.0,
            result.languages.len(),
            result.frameworks.len(),
            result.infrastructure_signals.len(),
        );
    }
}
