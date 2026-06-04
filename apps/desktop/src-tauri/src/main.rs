// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::{Arc, Mutex};
use tauri::{Manager, State};
use tauri_plugin_shell::ShellExt;

pub struct EngineSupervisor {
    child: Arc<Mutex<Option<tauri_plugin_shell::process::CommandChild>>>,
    pub port: u16,
    pub endpoint: String,
}

impl EngineSupervisor {
    pub fn start(app: &tauri::AppHandle) -> Result<Self, String> {
        let port = portpicker::pick_unused_port().ok_or("No available port")?;
        let endpoint = format!("http://127.0.0.1:{}", port);

        let shell = app.shell();
        let (mut rx, child) = shell
            .sidecar("lensfit-engine")
            .map_err(|e| format!("Failed to create sidecar: {}", e))?
            .args(["--port", &port.to_string(), "--mode", "desktop"])
            .spawn()
            .map_err(|e| format!("Failed to start engine: {}", e))?;

        // Spawn a thread to consume stdout/stderr so the pipe doesn't block
        tauri::async_runtime::spawn(async move {
            while let Some(event) = rx.recv().await {
                match event {
                    tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
                        println!("[engine stdout] {}", String::from_utf8_lossy(&line));
                    }
                    tauri_plugin_shell::process::CommandEvent::Stderr(line) => {
                        eprintln!("[engine stderr] {}", String::from_utf8_lossy(&line));
                    }
                    tauri_plugin_shell::process::CommandEvent::Error(e) => {
                        eprintln!("[engine error] {}", e);
                    }
                    tauri_plugin_shell::process::CommandEvent::Terminated(payload) => {
                        println!(
                            "[engine terminated] code={:?} signal={:?}",
                            payload.code, payload.signal
                        );
                    }
                    _ => {}
                }
            }
        });

        // Health check in background thread to avoid blocking main thread
        let health_url = format!("{}/health", endpoint);
        let (tx, rx) = std::sync::mpsc::channel();
        std::thread::spawn(move || {
            let client = reqwest::blocking::Client::builder()
                .timeout(std::time::Duration::from_millis(500))
                .build();
            let client = match client {
                Ok(c) => c,
                Err(e) => {
                    let _ = tx.send(Err(format!("Failed to build HTTP client: {}", e)));
                    return;
                }
            };

            let mut ready = false;
            for _ in 0..100 {
                if client.get(&health_url).send().is_ok() {
                    ready = true;
                    break;
                }
                std::thread::sleep(std::time::Duration::from_millis(100));
            }

            if ready {
                let _ = tx.send(Ok(()));
            } else {
                let _ = tx.send(Err("Engine health check timeout".into()));
            }
        });

        rx.recv()
            .map_err(|e| format!("Health check channel error: {}", e))?
            .map_err(|e| e)?;

        Ok(Self {
            child: Arc::new(Mutex::new(Some(child))),
            port,
            endpoint,
        })
    }

    pub fn shutdown(&self) {
        if let Ok(mut guard) = self.child.lock() {
            if let Some(child) = guard.take() {
                let _ = child.kill();
            }
        }
    }
}

impl Drop for EngineSupervisor {
    fn drop(&mut self) {
        self.shutdown();
    }
}

#[tauri::command]
fn get_engine_endpoint(state: State<'_, EngineSupervisor>) -> String {
    state.endpoint.clone()
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let supervisor = EngineSupervisor::start(&app.handle())?;
            app.manage(supervisor);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_engine_endpoint])
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|_app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                if let Some(supervisor) = _app_handle.try_state::<EngineSupervisor>() {
                    supervisor.shutdown();
                }
            }
        });
}
