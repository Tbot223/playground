use std::io::Result;
use serde_json;
use std::fs;
use std::path::PathBuf;
use std::env;
use std::collections::HashMap;


struct Config {
    runtime_cwd: PathBuf,
    language_file_dir_path: PathBuf,
    language_file_extension: String,
}

struct Localizer {
    supported_languages: HashMap<String, PathBuf>,
    supported_languages_cache: HashMap<String, HashMap<String, String>>,
    lru_order: Vec<String>,
    sup_lang_cache_limit: usize,
}

impl Localizer {
    // Private Functions
    fn langs_cache_manager(&mut self, _key: &str, _lang: &str) -> Result<bool> {
        if self.supported_languages_cache.contains_key(_lang) {
            self.lru_order.retain(|l| l != _lang);
            self.lru_order.push(_lang.to_string());
            return Ok(true);
        } else if !self.supported_languages_cache.contains_key(_lang) {
            // Limit ignored, always add new lang.
            // Why? -> Adding new language caches and deleting existing ones will cause the cache capacity limit to be reached. 
            // The limit may be exceeded during this process, but the cache capacity will eventually converge exactly to the limit.
            self.lru_order.retain(|l| l != _lang);
            self.lru_order.push(_lang.to_string());
            let data: String = fs::read_to_string(self.supported_languages.get(_lang)
            .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "Language file not found"))?)?;
            let lang_map: HashMap<String, String> = serde_json::from_str(&data).map_err(|e| {
                std::io::Error::new(std::io::ErrorKind::InvalidData, format!("Failed to parse JSON: {}", e))
            })?;
            self.supported_languages_cache.insert(_lang.to_string(), lang_map);
            if self.supported_languages_cache.len() <= self.sup_lang_cache_limit as usize {
                return Ok(true);
            } else {
                let oldest_lang = self.lru_order.remove(0);
                self.supported_languages_cache.remove(&oldest_lang);
                return Ok(true);
            }
        } else if self.supported_languages.len() == 0 {
            eprintln!("No supported languages found.");
            return Ok(false);
        } else {
            eprintln!("Not expected situation in langs_cache_manager.");
            eprintln!("Clearing all caches.");
            self.supported_languages_cache.clear();
            self.lru_order.clear();
            return Ok(false);
        }
    }

    fn scan_languages(config: &Config) -> Result<HashMap<String, PathBuf>> {
        let lang_files: HashMap<String, PathBuf> = fs::read_dir(&config.language_file_dir_path)?
            .filter_map(|entry| {
                let entry: fs::DirEntry = entry.ok()?;
                let path = entry.path();
                if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some(config.language_file_extension.trim_start_matches('.')) {
                    let lang_code = path.file_stem().and_then(|s| s.to_str())?.to_string();
                    Some((lang_code, path))
                } else {
                    None
                }
            })
            .collect();
        Ok(lang_files)
    }

    // Public Functions
    pub fn new() -> Result<(Localizer, Config)> {

        let ldsp = PathBuf::from("./languages/");
        match fs::create_dir_all(&ldsp) {
            Ok(_) => {},
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {},
            Err(e) => return Err(e),
        }
        let ldsp = fs::canonicalize(&ldsp)?;

        let config = Config {
            runtime_cwd: env::current_dir()?,
            language_file_dir_path: ldsp.clone(),
            language_file_extension: String::from(".json"),
        };

        if !config.language_file_dir_path.exists() {
            fs::create_dir_all(&config.language_file_dir_path)?;
        }
        let _lang_files: HashMap<String, PathBuf> = Localizer::scan_languages(&config)?;

        println!("Language files found: {}", _lang_files.len());
        let localizer = Localizer {
            supported_languages: _lang_files,
            supported_languages_cache: HashMap::new(),
            lru_order: Vec::new(),
            sup_lang_cache_limit: 5,
        };

        return Ok((localizer, config));
    }

    pub fn get_supported_languages(&self) -> Result<Vec<String>> {
        Ok(self.supported_languages.iter().filter_map(
            |(lang_code, path)| {
                if path.exists() {
                    Some(lang_code.clone())
                } else {
                    None
                }
            }
        ).collect())
    }

    pub fn get_text_by_key(&mut self, _key: &str, mut _lang: &str, fallback: &str) -> Result<String> {
        let effective_fallback = if fallback != "" && !self.supported_languages.contains_key(_lang) {
            fallback
        } else {
            "en-GB"
        };

        let effective_lang = if self.supported_languages.contains_key(_lang) {
            _lang
        } else {
            effective_fallback
        };

        let passing = self.langs_cache_manager(_key, effective_lang)?;
        let lang_map = &self.supported_languages_cache.get(effective_lang)
        .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "Language not found in cache"))?;

        if passing {
            if lang_map.contains_key(_key) {
                return Ok(lang_map.get(_key).ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "Key not found in language map"))?.to_string());
            } else {
                return Err(std::io::Error::new(std::io::ErrorKind::NotFound, "Key not found in language map"));
            } 
        } else {
            return Err(std::io::Error::new(std::io::ErrorKind::Other, "Failed to manage language cache"));
        }
    }

    pub fn rescan_languages(&mut self, config: &Config) -> Result<bool> {
        let _lang_files: HashMap<String, PathBuf> = Localizer::scan_languages(config)?;
        self.supported_languages = _lang_files;

        for lang in self.supported_languages.keys() {
            self.supported_languages_cache.remove(lang);
            self.lru_order.retain(|l| l != lang);
        }
        Ok(true)
    }

    pub fn reload_language(&mut self, _lang: &str) -> Result<bool> {
        if self.supported_languages.contains_key(_lang) {
            self.supported_languages_cache.remove(_lang);
            self.lru_order.retain(|l| l != _lang);
            
            self.langs_cache_manager("", _lang)?;
            Ok(true)
        } else {
            Err(std::io::Error::new(std::io::ErrorKind::NotFound, "Language not supported"))
        }
    }

    pub fn reload_all(&mut self, config: &Config) -> Result<bool> {
        self.supported_languages_cache.clear();
        self.lru_order.clear();
        self.rescan_languages(config)?;
        Ok(true)
    }
}

fn main() { 
    match Localizer::new() {
        Ok((mut _localizer, _config)) => {
            println!("\nLocalizer initialized successfully.\n");
            println!("Supported languages:");
            for (lang_code, path) in &_localizer.supported_languages {
                println!("Language Code: {}, File Path: {}", lang_code, path.display());
            }

            println!("\nSupported languages map: {:?}\n", &_localizer.supported_languages);
            println!("Current working directory: {}\n", _config.runtime_cwd.display());


            println!("get_supported_languages() output:");
            match _localizer.get_supported_languages() {
                Ok(langs) => {
                    for lang in langs {
                        println!(" - {}", lang);
                    }
                }
                Err(e) => {
                    eprintln!("Error retrieving supported languages: {}", e);
                }
            }

            match _localizer.get_text_by_key("greeting", "en-lm", "en-GB") {
                Ok(text) => {
                    println!("\nText for key 'greeting' in 'en-GB': {}", text);
                }
                Err(e) => {
                    eprintln!("Error retrieving text by key: {}", e);
                }
            }

            match _localizer.rescan_languages(&_config) {
                Ok(_) => {
                    println!("\nRescanned languages successfully.");
                }
                Err(e) => {
                    eprintln!("Error rescanning languages: {}", e);
                }
            }

            match _localizer.reload_language("en-GB") {
                Ok(_) => {
                    println!("\nReloaded language '{}' successfully.", "en-GB");
                }
                Err(e) => {
                    eprintln!("Error reloading language '{}': {}", "en-GB", e);
                }
            }

            match _localizer.reload_all(&_config) {
                Ok(_) => {
                    println!("\nReloaded all languages successfully.");
                }
                Err(e) => {
                    eprintln!("Error reloading all languages: {}", e);
                }
            }

            match _localizer.get_text_by_key("farewell", "en-UN", "en-GB") {
                Ok(text) => 
                    println!("\nText for key 'farewell' in 'en-UN' with fallback to 'en-GB': {}", text);
                }
                Err(e) => {
                    eprintln!("Error retrieving text by key: {}", e);
                }
            }
        }
        Err(e) => {
            eprintln!("Failed to initialize Localizer: {}", e);
            eprintln!("\n\n치명적 오류 발생! 프로그램을 종료합니다.\n\n");
            std::process::exit(1);
        }
    }
}