String inString = ""; 

#define PIN1 5

void setup() {
  pinMode(PIN1, OUTPUT);
  // put your setup code here, to run once:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  
}

void loop() {
  while (Serial.available() > 0) {
    int inChar = Serial.read();
    if (isDigit(inChar)) {
      // convert the incoming byte to a char and add it to the string:
      inString += (char)inChar;
    }
    // if you get a newline, print the string, then the string's value:
    if (inChar == '\n') {
      int val = inString.toInt();
      
      //Serial.println(inString.toInt());
      analogWrite(PIN1, constrain(val, 0, 254));
      // clear the string for new input:
      inString = "";
    }
  }
}
