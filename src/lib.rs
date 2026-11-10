//! Popamp's default skin, for the player to compile in.
//!
//! The skin is the `skin.toml` and the SVG files at the top of this
//! repository; this crate only hands their bytes to the player.

macro_rules! files {
    ($($f:literal),*) => { &[$(($f, include_bytes!(concat!("../", $f)) as &[u8])),*] };
}

/// Every file of the skin: its name inside the skin and its bytes.
pub const FILES: &[(&str, &[u8])] = files!(
    "skin.toml",
    "main.svg",
    "cbuttons.svg",
    "titlebar.svg",
    "shufrep.svg",
    "text.svg",
    "volume.svg",
    "balance.svg",
    "monoster.svg",
    "playpaus.svg",
    "numbers.svg",
    "posbar.svg",
    "eqmain.svg",
    "eq_ex.svg",
    "pledit.svg"
);

#[cfg(test)]
mod tests {
    use super::FILES;

    /// A picture added to the skin but not to `FILES` would be missing
    /// from the player.
    #[test]
    fn every_picture_in_the_folder_is_listed() {
        let mut on_disk: Vec<String> = std::fs::read_dir(env!("CARGO_MANIFEST_DIR"))
            .unwrap()
            .map(|e| e.unwrap().file_name().to_string_lossy().into_owned())
            .filter(|n| n.ends_with(".svg") || n == "skin.toml")
            .collect();
        let mut listed: Vec<String> = FILES.iter().map(|(n, _)| n.to_string()).collect();
        on_disk.sort();
        listed.sort();
        assert_eq!(on_disk, listed);
    }

    /// `skin.toml` names its pictures as `"<name>.svg"`.
    #[test]
    fn every_picture_skin_toml_names_is_listed() {
        let toml = std::str::from_utf8(FILES[0].1).unwrap();
        let named: Vec<&str> = toml.split('"').filter(|s| s.ends_with(".svg")).collect();
        assert!(!named.is_empty());
        for name in named {
            assert!(FILES.iter().any(|(n, _)| *n == name), "{name} is not in FILES");
        }
    }
}
