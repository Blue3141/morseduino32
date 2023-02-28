



# Morseduino32
#### A compact ESP32-based morse code transceiver
## Introduction
The Morseduino32 is a device which allows to send and receive Morse code to and from another Morseduino32, through the ESP-NOW protocol; the final goal is to implement an online server to send the Morse code through the Internet. The project is still a work-in-progress, so please be patient!

#### Roadmap
☒ Build the first prototype
☒ Test the hardware
~~☒ Build the second prototype~~ *high voltage during the recharge broke the LILYGO*
☒ Build, train and test on KNIME the Neural Network (LSTM RNN) to decode the signal
☒ Convert the NN to a TFLite model (suitable for ESP32)
☐ Test the NN on the Morseduino
☐ Build the second prototype (again)
☐ Implement the ESP-NOW protocol
☐ Test inter-device communication
☐ Implement a decent UI
☐ Implement WiFi communication through Firebase

## Hardware
### Components
This device is built from scratch with the following components:
- 1 x LILYGO TTGO T-Display (CH9122F) with battery connector
- 1 x Box (I used the packaging box of the LILYGO)
- 1 x RGB led module, 10mm radius (140c5)
- 1 x rotary encoder
- 1 x Li-ion battery, 3.7V 2000mAh
- 1 x 10kOhm resistor
- 1 x keyboard switch (a button gets the job done too)
- 1 x on-off switch (rocker switch)
- 1 x active buzzer module
- Wire, soldering kit, pliers, heat shrinkable tubing, electrical tape, cutter, and a lot of patience

### Assembling
The wire diagram is the following:

![Wire Diagram](/media/wire_diagram.jpg "Wire Diagram")

The suggested soldering order is:
1.  Buzzer
2.  Rotary Encoder
3.  Led
4.  Switch
5.  Battery and rocker switch

I will upload more specific instructions soon!

## Software
### Overview
The software can be divided in two main parts:
- the main Morseduino32 program, which actually reads the sensors and manages all the logic of the device;
- the Neural Network which enables the decoding, which is created and trained on an external computer and then loaded on the Morseduino32.

### The Neural Network
The Neural Network is built, trained and tested in KNIME. To decode morse code signals I opted for a Recurrent Neural Network.
This choice is based on the need, for the network, to decode morse code with unstable signal speed, and to manage different sequence lengths.

The NN has to decode a message, which is a sequence of signals. The signal is a period of time of a certain duration (saved in milliseconds), in which the button has been pressed (high signal) or not (low signal).
Every signal (characterized by duration and type) has to be decoded with one of the following symbols:

| Symbol | Meaning | Relative duration | Signal type |
| ------------ | ------------ |
| .  | a dit |1 |High (1) |
| -  |  a dah|3 | High (1)|
| * |   an intra-character space |1 | Low (0)|
| &#124; |   an inter-character space | 3|Low (0) |
|  / |  a word space | 7| Low (0)|
| _ |  a "missing symbol" character|0 |Low (0) |

The last one is for used for padding (read below).

#### Structure
The structure of the network is rather simple - it must be small enough to run smoothly on the Morseduino32.
##### Input Layer
As shown in the image, the first layer takes as input a length-limited sequence of morse code signals.

To decode a signal, the previous 9 (and the current, which will be translated) are taken into account, to consider the local speed. 10 signals equal to approximately a couple of alphanumeric characters (in the translated message).

The morse code message is a sequence of signals: due to the fact that a message starts with the '-.-.-' prosign (shorthand sequences of signals to simplify the communication; this prosign means *"starting communication"*), which has 5 high signal and 4 low signals, the NN has 9 signals available which do not need to be translated.
This is an advantage, because this first signals are used as initial "memory data" for the first real signal of the message, thus componing the 10-signal vector needed for decoding.

In conclusion, the input layer will always have a sequence of 10 signals, and will have to decode the last one.

##### LSTM Layer
The LSTM Layer is the core of the NN. It has 10 "cells", one for each time-step (signal) considered; each cell filters the input of the previous cell, takes the correspondent signal, and decides what to remember from the input, what to forget, and what to add to the memory. This processed data is then sent to the next cell. The hidden state has dimension 100, meaning each cell will output a hidden state vector of 100 units to the next cell.

##### Dense Layer
The Dense Layer has a single unit; it takes as input the last LSTM cell hidden state vector and it gives a double value as output. The rounded value is the code of the symbol to use

#### Training
The training uses batches of 512 elements and does 50 epochs.

##### The dataset
I had to create a custom dataset to train the NN. The jupyter notebook dataset_generator contains a python program to generate such a dataset, with customizable parameters. Strangely (but not that much) generating a good dataset was harder than building the NN.

The main idea is that, given a morse code text (like "-.-. .. .- ---") and the initial speed of the transmission (in WPM, which then can be translated as a "dit unit"), the speed changes depending on a function. Instead of using an acceleration function (speed variation over time), I found that generating a function which indicates the percentual variation is easier and more manageable, while still allowing a lot of complex variations patterns.

The speed function is generated by adding some local sinusoids, which affect the local speed (letter- and word-level), and some larger period sinusoids, which affect the general speed of the transmission (sentence-level). All the parameters (amplitudes, periods, phases, number of sinusoid used) are generated randomly and completely customizable.

The function is then "noised" using a random, normal-distributed value for each x.

The sequence generation is parametric too; the number of sequences and the max sequence length must be specified.

#### Some experiments
If creating NN was a perfect art, it would not be interesting...

##### Different sequence lengths
I tried to train the model with different input sequence length.















R^2

mean absolute error

mean squared error

root mean squared error

mean signed difference

mean absolute percentage error

adjusted R^2

0.9572839860884703

0.03930000000000003

0.05609999999999999

0.2368543856465402

-0.007899999999999992

0.018600000000000002

0.9572839860884703
