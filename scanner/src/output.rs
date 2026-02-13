use serde::Serialize;

#[derive(Debug, Serialize, Clone)]
pub struct ScanResult {
    pub languages: Vec<LanguageEntry>,
    pub frameworks: Vec<SignalEntry>,
    pub project_structures: Vec<String>,
    pub infrastructure_signals: Vec<SignalEntry>,
}

#[derive(Debug, Serialize, Clone)]
pub struct LanguageEntry {
    pub name: String,
    pub category: String,
    pub percentage: f64,
}

#[derive(Debug, Serialize, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct SignalEntry {
    pub name: String,
    pub category: String,
}
