import SwiftUI

@main
struct KantoGridMacApp: App {
    var body: some Scene {
        WindowGroup("National Pokedex Grid") {
            ContentView()
                .frame(minWidth: 1180, minHeight: 760)
        }
        .windowResizability(.contentSize)
    }
}
