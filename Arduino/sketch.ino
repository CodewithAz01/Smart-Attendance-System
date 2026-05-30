#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);

// Output pins
const int GREEN_LED = 6;
const int RED_LED = 7;
const int BUZZER = 5;

String receivedMessage = "";

void setup()
{
    Serial.begin(9600);

    SPI.begin();
    rfid.PCD_Init();

    pinMode(GREEN_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(BUZZER, OUTPUT);

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, LOW);
    digitalWrite(BUZZER, LOW);

    Serial.println("System ready. Waiting for RFID card...");
}

void loop()
{
    // -------------------------------
    // RFID Detection
    // -------------------------------
    if (rfid.PICC_IsNewCardPresent() &&
        rfid.PICC_ReadCardSerial())
    {
        String uid = "";

        for (byte i = 0; i < rfid.uid.size; i++)
        {
            uid += String(rfid.uid.uidByte[i]);
        }

        Serial.println(uid);

        rfid.PICC_HaltA();
        rfid.PCD_StopCrypto1();
    }

    // -------------------------------
    // Commands from Python
    // -------------------------------
    if (Serial.available())
    {
        receivedMessage = Serial.readStringUntil('\n');
        receivedMessage.trim();

        if (receivedMessage == "AUTHORIZED")
        {
            authorizedSignal();
        }
        else if (receivedMessage == "UNAUTHORIZED")
        {
            unauthorizedSignal();
        }
    }
}

// ===================================
// Authorized Access
// ===================================
void authorizedSignal()
{
    digitalWrite(GREEN_LED, HIGH);

    tone(BUZZER, 1000);
    delay(150);
    noTone(BUZZER);

    delay(1500);

    digitalWrite(GREEN_LED, LOW);
}

// ===================================
// Unauthorized Access
// ===================================
void unauthorizedSignal()
{
    for (int i = 0; i < 3; i++)
    {
        digitalWrite(RED_LED, HIGH);

        tone(BUZZER, 500);
        delay(300);

        digitalWrite(RED_LED, LOW);

        noTone(BUZZER);
        delay(200);
    }
}
