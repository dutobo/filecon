const COMMANDS: &[&str] = &["resolve", "icon", "icon_for_path"];

fn main() {
    tauri_plugin::Builder::new(COMMANDS).build();
}
