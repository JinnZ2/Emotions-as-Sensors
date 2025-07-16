// sensor_array.ino

// Pulse sensor on analog pin A0
const int pulsePin = 36; // VP
int pulseVal = 0;
unsigned long lastBeat = 0;
int bpm = 0;

// GSR on analog pin A1
const int gsrPin = 39; // VN
int gsrVal = 0;

// Mic on analog pin A2 (simple analog mic)
const int micPin = 34;
int micLevel = 0;

// For BLE, serial, or display
void setup() {
  Serial.begin(115200);
}

void loop() {
  pulseVal = analogRead(pulsePin);
  gsrVal = analogRead(gsrPin);
  micLevel = analogRead(micPin);

  // ---- HRV and BPM Simulation ----
  unsigned long now = millis();
  static unsigned long lastPulseTime = 0;

  if (pulseVal > 600 && (now - lastPulseTime > 300)) {
    bpm = 60000 / (now - lastPulseTime);
    lastPulseTime = now;
  }

  // ---- Symbolic Mapping ----
  String HRV_state = bpm > 55 && bpm < 85 ? "φ" : "⚠";
  String GSR_state = gsrVal > 400 ? "⚡" : "△";
  String Voice_state = micLevel > 700 ? "❄" : "○";

  String system_status = "🟢";
  if (GSR_state == "⚡" || Voice_state == "❄") system_status = "🟠";
  if (HRV_state == "⚠" && GSR_state == "⚡" && Voice_state == "❄") system_status = "🔴";

  // ---- Print Output ----
  Serial.println("{");
  Serial.print("\"HRV_state\": \""); Serial.print(HRV_state); Serial.println("\",");
  Serial.print("\"GSR_state\": \""); Serial.print(GSR_state); Serial.println("\",");
  Serial.print("\"Voice_tone\": \""); Serial.print(Voice_state); Serial.println("\",");
  Serial.print("\"System_status\": \""); Serial.print(system_status); Serial.println("\"");
  Serial.println("}");

  delay(2000);  // Every 2 seconds
}
