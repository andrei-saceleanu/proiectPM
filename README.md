# ProiectPM

https://ocw.cs.pub.ro/courses/pm

Proiectul consta in preluarea informatiilor generate de senzorul de distanta ultrasonic HC-SR04+(+ senzor de temperatura si umiditate DHT11)/un fotorezistor si transmiterea unor comenzi de executat de la microcontroller la PC,prin intermediul interfetei seriale.

1. System volume

  Volumul sistemului este controlat conform cu magnitudinea distantei de la senzor la primul obstacol intalnit.Un range prestabilit [MIN_DIST,MAX_DIST] se mapeaza la un procent de volum.In contextul pycaw,functia de setare necesita o valoare de amplificare specificata in decibeli.Valorile preluate de la https://www.codestudyblog.com/cs2112pyc/1221175124.html au fost alese datorita potrivirii cu sistemul de implementare/testare.Nu s-a optat pentru o ecuatie de interpolare a valorilor deoarece diferitele ecuatii logaritmice obtinute aveau erori prea mari si nu setau volumul corespunzator.
  
2. System brightness

  Luminozitatea sistemului este modificata conform cu distanta inregistrata de HC-SR04+.Acelast range prestabilit se mapeaza la un procent de luminozitate.

3. Media control

  Operarea in acest mod lanseaza un video prestabilit(o extensie naturala ar fi citirea numelui fisierului video de la tastatura) iar distanta furnizata de senzor va trimite utilizatorul la o anumita pozitie in cadrul video-ului(exprimata in procente din lungimea totala).Modificarea modului de operare prin apasarea butonului inchide fereastra de redare.In caz de finalizare a video-ului,o noua comanda valida(distanta in range-ul prestabilit) va initializa o fereastra noua. 
  Interactiunea cu fisierul video utlizeaza standard-ul VLC.
  
4. System brightness(adaptive)

  Luminozitatea sistemului este modificata direct proportional cu luminozitatea ambientala,cuantificata prin valoarea analogica de la un divizor de tensiune cu un fotorezistor si convertita digital cu ajutorul ADC-ului placutei Arduino.
