#include <Servo.h>

Servo motor_kontrol;

void setup() {
  motor_kontrol.attach(9);
  Serial.begin(9600);
  
  // Test: Açılışta 90'a gidip 0'a dönsün (Sağlamlık kontrolü)
  motor_kontrol.write(90);
  delay(500);
  motor_kontrol.write(0);
}

void loop() {
  if (Serial.available() > 0) {
    char gelen_karakter = Serial.read(); // Veriyi karakter olarak oku

    if (gelen_karakter == '1') {
      motor_kontrol.write(90);
    } 
    else if (gelen_karakter == '0') {
      motor_kontrol.write(0);
    }
  }
}