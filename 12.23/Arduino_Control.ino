#include <Car_Library.h>

int motorC1 = 2;
int motorC2 = 3;
int motorA1 = 4;    // 모터 드라이버 IN1
int motorA2 = 5;    // 모터 드라이버 IN2
int motorB1 = 7;    // 모터 드라이버 IN1
int motorB2 = 6;    // 모터 드라이버 IN2


int val=0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);       // 시리얼 통신 시작, 통신 속도 설정
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
  pinMode(motorC1, OUTPUT);
  pinMode(motorC2, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()) {
    val = Serial.parseInt();

    if(val == 0) {
      motor_hold(motorC1, motorC2);
      motor_hold(motorA1, motorA2);
      motor_hold(motorB1, motorB2);
    }
    if(val == 1) {
      motor_hold(motorC1, motorC2);
      motor_forward(motorA1, motorA2,50);
      motor_forward(motorB1, motorB2,50);
    }
    if(val == 2) {
      motor_hold(motorC1, motorC2);
      motor_forward(motorA1, motorA2,100);
      motor_forward(motorB1, motorB2,100);
    }
    
  }
}
