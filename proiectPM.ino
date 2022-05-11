#include <NewPing.h>
#include <DHT.h>

#define BUTTON PD7
#define LEDR 9
#define LEDG 10
#define LEDB 11
#define NO_MODES 4
#define TRIG 4
#define ECHO 5
#define MAX_DISTANCE 26
#define DHTPIN 2
#define DHTTYPE DHT11
#define PHOTORES A0

unsigned int operatingMode;
unsigned int ledState;
unsigned long int intervalStart, ts, ts_analog;
unsigned int debounceDelay, intervalCommand;
float duration, distance, hum, temp;
NewPing sonar(TRIG, ECHO, MAX_DISTANCE);
DHT dht(DHTPIN, DHTTYPE);

// setare TIMER1 pentru frecventa intreruperi 1 Hz in mod CTC
void configure_timer(){
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  OCR1A = 15625;
  TCCR1B |= (1 << WGM12) | (1 << CS12) | (1 << CS10);
}

void init_timer(){
  TIMSK1 |= (1 << OCIE1A);
}

// rutina de tratare a intreruperii face toggle la starea LED-ului
ISR(TIMER1_COMPA_vect){
  ledState = !ledState;
}

// fiecare mod de operare(exceptie luminozitate adaptiva) este
// indicat printr-o culoare distincta a LED-ului in blinking
void blinkLED(){
  if(ledState == 0){
    analogWrite(LEDR,0);
    analogWrite(LEDG,0);
    analogWrite(LEDB,0);
  }else{
    switch(operatingMode){
      case 0:
        analogWrite(LEDR,255);
        analogWrite(LEDG,0);
        analogWrite(LEDB,0);
        break;
      case 1:
        analogWrite(LEDR,0);
        analogWrite(LEDG,255);
        analogWrite(LEDB,0);
        break;
      case 2:
        analogWrite(LEDR,0);
        analogWrite(LEDG,0);
        analogWrite(LEDB,255);
        break;
      default:
        break;  
    }
  }
}

// setare Pin Change interrupt pentru butonul conectat la pinul 7/PD7
void configure_button(){
  PCICR |= (1 << PCIE2);
  PCMSK2 |= (1 << PCINT23);
}

// apasarea butonului duce la modificarea modului de operare
ISR(PCINT2_vect){
  if (millis() - intervalStart > debounceDelay){
    intervalStart = millis();
    if ((PIND & (1 << BUTTON)) == 0) {
      operatingMode = (operatingMode + 1) % NO_MODES;
    }
  }
}

void setup() {
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);
  
  ledState = 0;
  debounceDelay = 200;
  intervalStart = 0;
  operatingMode = 0;
  intervalCommand = 1000;
  ts = 0;
  ts_analog = 0;
  
  cli();
  configure_timer();
  init_timer();
  configure_button();
  sei();
  Serial.begin(9600);
  dht.begin();
}

// functia calculeaza viteza sunetului conform cu conditiile
// ambientale inregistrate de senzorul DHT11
float calculateSpeed(){
  hum = dht.readHumidity();
  temp= dht.readTemperature();

  float sp = 331.4 + (0.606 * temp) + (0.0124 * hum);
  sp /= 10000;
  return sp;
}

// functia calculeaza distanta de la senzorul ultrasonic la
// primul obstacol intalnit si genereaza comanda pe seriala,
// catre PC
// pentru a atenua zgomotul datelor citite,durata drumului
// pulsului ultrasonic este considerata a fi mediana a
// 5 inregistrari succesive
void calculateDistance(){
  float soundSpeed = calculateSpeed();
  duration = sonar.ping_median(5);  
  distance = (duration / 2) * soundSpeed;

  switch(operatingMode){
    case 0:
      Serial.print("volume:");
      break;
    case 1:
      Serial.print("brightness:");
      break;
    case 2:
      Serial.print("video:");
      break;
    default:
      break;
  }
  Serial.println(distance);
}

// pentru primele 3 moduri de operare,se realizeaza blinking LED
// si calculul distantei
// pentru modul adaptiv, valoarea convertita de ADC se preia
// de pe pinul PHOTORES(A0) si se transmite catre PC
// + se da clear pe LED
// frecventa de efectuare a operatiilor a fost stabilita
// la intervalCommand = 1000 ms = 1 s
void loop() {
  if(operatingMode <= 2){
    blinkLED();
    if(millis() - ts >= intervalCommand){
      ts = millis();
      calculateDistance();
    }
  }else{
    analogWrite(LEDR,0);
    analogWrite(LEDG,0);
    analogWrite(LEDB,0);
    if(millis() - ts_analog >= intervalCommand){
      ts_analog = millis();
      int val = analogRead(PHOTORES);
      Serial.print("adaptive:");
      Serial.println(val);
    } 
  }
}
