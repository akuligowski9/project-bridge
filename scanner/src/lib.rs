pub mod dependencies;
pub mod frameworks;
pub mod languages;
pub mod output;
pub mod scan;
pub mod structures;

pub use output::ScanResult;
pub use scan::{scan_directories, scan_directory};
