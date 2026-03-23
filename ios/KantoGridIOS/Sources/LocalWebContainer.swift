import SwiftUI
import WebKit

struct LocalWebContainer: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.allowsBackForwardNavigationGestures = true

        loadIndex(into: webView)
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    private func loadIndex(into webView: WKWebView) {
        guard let webRoot = Bundle.main.resourceURL?.appendingPathComponent("Web"),
              let indexURL = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "Web")
        else {
            webView.loadHTMLString(
                """
                <html>
                  <body style="font-family: -apple-system; background: #081019; color: #e6fbff; padding: 24px;">
                    <h1>Missing Web Bundle</h1>
                    <p>Run scripts/sync_web_bundle.sh and add the Web folder to the app target as a folder reference.</p>
                  </body>
                </html>
                """,
                baseURL: nil
            )
            return
        }

        webView.loadFileURL(indexURL, allowingReadAccessTo: webRoot)
    }
}
