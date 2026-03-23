import SwiftUI

@main
struct KantoGridMacApp: App {
    var body: some Scene {
        WindowGroup("Kanto Grid 151") {
            ContentView()
                .frame(minWidth: 1180, minHeight: 760)
        }
        .windowResizability(.contentSize)
    }
}
