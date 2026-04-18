/**
 * ArcticSecurityShield - Gmail Add-on
 * Scans the current email for phishing signals.
 *
 * Setup:
 *   1. Go to script.google.com -> New project
 *   2. Paste this code, save
 *   3. Run setupTrigger() once to authorise
 *   4. Deploy -> Test deployments -> Gmail add-on
 */

// Paste your ngrok URL here each time you start ngrok
// e.g. "https://a1b2-81-82-123-45.ngrok-free.app"
var FLASK_URL = "https://YOUR-NGROK-URL.ngrok-free.app";


// ── Entry point: called when user opens an email ──────────────────────────────

function buildAddOn(e) {
  var message     = getCurrentMessage(e);
  var subject     = message.getSubject();
  var body        = message.getPlainBody();
  var sender      = message.getFrom();
  var preview     = body.substring(0, 300).replace(/\n/g, " ");

  return CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle("ArcticSecurityShield")
        .setSubtitle("Phishing detector")
    )
    .addSection(
      CardService.newCardSection()
        .addWidget(
          CardService.newTextParagraph()
            .setText("<b>From:</b> " + sender + "<br><b>Subject:</b> " + subject)
        )
        .addWidget(
          CardService.newButtonSet()
            .addButton(
              CardService.newTextButton()
                .setText("Scan this email")
                .setOnClickAction(
                  CardService.newAction()
                    .setFunctionName("scanEmail")
                    .setParameters({
                      "body":   body.substring(0, 2000),
                      "sender": sender
                    })
                )
            )
        )
    )
    .build();
}


// ── Scan handler: sends email to Flask, shows result ─────────────────────────

function scanEmail(e) {
  var body   = e.parameters.body;
  var sender = e.parameters.sender;

  var result = callFlask(body, sender);

  if (result.error) {
    return showError(result.error);
  }

  return showResult(result);
}


// ── Build result card ─────────────────────────────────────────────────────────

function showResult(r) {
  var colors = {
    "high":   { bg: "#FFEBEE", text: "#C62828", label: "HIGH RISK"   },
    "medium": { bg: "#FFF3E0", text: "#E65100", label: "MEDIUM RISK" },
    "low":    { bg: "#E8F5E9", text: "#2E7D32", label: "LOW RISK"    },
  };
  var c = colors[r.risk_level] || colors["low"];

  var section = CardService.newCardSection();

  // Risk badge
  section.addWidget(
    CardService.newDecoratedText()
      .setTopLabel("Result")
      .setText(c.label + "  –  " + r.probability + "% phishing probability")
  );

  // Explanation
  section.addWidget(
    CardService.newTextParagraph()
      .setText("<i>" + r.explanation + "</i>")
  );

  // Flags
  if (r.flags && r.flags.length > 0) {
    var flagText = "<b>Signals found:</b><br>";
    r.flags.forEach(function(f) {
      if (typeof f === "string") {
        flagText += "• " + f + "<br>";
      } else {
        flagText += "• <b>" + f.category + ":</b> " + f.detail + "<br>";
      }
    });
    section.addWidget(
      CardService.newTextParagraph().setText(flagText)
    );
  } else {
    section.addWidget(
      CardService.newTextParagraph()
        .setText("No suspicious signals found.")
    );
  }

  // Model used
  section.addWidget(
    CardService.newTextParagraph()
      .setText("<font color='#888888'>Model: " + r.model_used + "</font>")
  );

  // Scan again button
  section.addWidget(
    CardService.newButtonSet()
      .addButton(
        CardService.newTextButton()
          .setText("Back")
          .setOnClickAction(
            CardService.newAction()
              .setFunctionName("buildAddOn")
          )
      )
  );

  return CardService.newActionResponseBuilder()
    .setNavigation(
      CardService.newNavigation()
        .pushCard(
          CardService.newCardBuilder()
            .setHeader(
              CardService.newCardHeader()
                .setTitle("ArcticSecurityShield")
                .setSubtitle(c.label)
            )
            .addSection(section)
            .build()
        )
    )
    .build();
}


// ── Error card ────────────────────────────────────────────────────────────────

function showError(msg) {
  return CardService.newActionResponseBuilder()
    .setNavigation(
      CardService.newNavigation()
        .pushCard(
          CardService.newCardBuilder()
            .setHeader(
              CardService.newCardHeader().setTitle("Connection error")
            )
            .addSection(
              CardService.newCardSection()
                .addWidget(
                  CardService.newTextParagraph()
                    .setText(
                      "Could not reach ArcticSecurityShield.<br><br>" +
                      "<b>Check:</b><br>" +
                      "1. Flask app is running (python app/arcticsecurityshield_app.py)<br>" +
                      "2. ngrok is running (ngrok http 5000)<br>" +
                      "3. FLASK_URL in Code.gs matches your current ngrok URL<br><br>" +
                      "<font color='#888'>Error: " + msg + "</font>"
                    )
                )
            )
            .build()
        )
    )
    .build();
}


// ── HTTP call to Flask ────────────────────────────────────────────────────────

function callFlask(body, sender) {
  try {
    var payload = JSON.stringify({ text: body, sender: sender });
    var options = {
      method:      "post",
      contentType: "application/json",
      payload:     payload,
      muteHttpExceptions: true,
    };
    var response = UrlFetchApp.fetch(FLASK_URL + "/predict/email", options);
    var code     = response.getResponseCode();

    if (code !== 200) {
      return { error: "Server returned " + code };
    }

    return JSON.parse(response.getContentText());

  } catch (err) {
    return { error: err.message };
  }
}


// ── Helper ────────────────────────────────────────────────────────────────────

function getCurrentMessage(e) {
  var accessToken = e.messageMetadata.accessToken;
  var messageId   = e.messageMetadata.messageId;
  GmailApp.setCurrentMessageAccessToken(accessToken);
  return GmailApp.getMessageById(messageId);
}
