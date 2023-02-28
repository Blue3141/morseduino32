



# Morseduino32
A compact ESP32-based, RNN-powered morse code transceiver
![morseduino32](/media/morseduino32.jpg "morseduino32")

## Introduction
The Morseduino32 is a device which allows to send and receive Morse code to and from another Morseduino32, through the ESP-NOW protocol; the final goal is to implement an online server to send the Morse code through the Internet. The project is still a work-in-progress, so please be patient!

#### Roadmap
- ☒ Build the first prototype
- ☒ Test the hardware
- ~~☒ Build the second prototype~~ *high voltage during the recharge broke the LILYGO*
- ☒ Build, train and test on KNIME the Neural Network (LSTM RNN) to decode the signal
- ☒ Convert the NN to a TFLite model (suitable for ESP32)
- ☐ Test the NN on the Morseduino
- ☐ Build the second prototype (again)
- ☐ Implement the ESP-NOW protocol
- ☐ Test inter-device communication
- ☐ Implement a decent UI
- ☐ Implement WiFi communication through Firebase

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
- the main Morseduino32 program, which reads the sensors and manages all the logic on the device;
- the Neural Network which allows the message decoding, which is created and trained on an external computer and then loaded on the Morseduino32.

### The Neural Network
The Neural Network is built, trained and tested in KNIME. To decode morse code signals I opted for a Recurrent Neural Network.
This choice is based on the need, for the network, to decode morse code with unstable signal speed, and to manage different sequence lengths.

![Keras Model](/media/keras_model.png "Keras Model")

The NN has to decode a message, which is a sequence of signals. The signal is a period of time of a certain duration (saved in milliseconds), in which the button has been pressed (high signal) or not (low signal).
Every signal (characterized by duration and type) has to be decoded with one of the following symbols:

| Symbol | Meaning | Relative duration | Signal type |
| ---|---|--- | --- |
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

#### Training and validation
The training uses batches of 512 elements and does 50 epochs. It uses the default training-loss based learing rate reduction and MSE as loss function.

##### The dataset
I had to create a custom dataset to train the NN. The jupyter notebook dataset_generator contains a python program to generate such a dataset, with customizable parameters. Strangely (but not that much) generating a good dataset was harder than building the NN.

The main idea is that, given a morse code text (like "-.-. .. .- ---") and the initial speed of the transmission (in WPM, which then can be translated as a "dit unit"), the speed changes depending on a function. Instead of using an acceleration function (speed variation over time), I found that generating a function which indicates the percentual variation is easier and more manageable, while still allowing a lot of complex variations patterns.

The speed function is generated by adding some local sinusoids, which affect the local speed (letter- and word-level), and some larger period sinusoids, which affect the general speed of the transmission (sentence-level). All the parameters (amplitudes, periods, phases, number of sinusoid used) are generated randomly and completely customizable. The periods of the sinusoid are chosen between prime numbers to maximize the total sinusoid period, thus improving the quality and diversity of the speed functions.

The function is then "noised" using a random, normal-distributed value for each x. 

![Function example](/media/function_example.png "Function example")

The sequence generation is parametric too; the number of sequences in the dataset and the max sequence length must be specified. A sample message is created, then a sliding window whose length is the desired sequence length generates the sequences. When the sample message is "fully scrolled", a new sample is generated.

It is possible to generate variable length sequences, given an upper bound to the length, by setting the parameter "ALWAYS_MAX_LENGTH" to False. The generated sequences will already have the necessary padding ('_' character).

This repository contains the jupyter notebook which generates the dataset, and two dataset used to train two different models. One uses fixed sequence length, the other uses sequences of variable length.

#### Some experiments
If creating NN was a perfect art, it would not be interesting...
##### LTSM Hidden State dimension
The dimension of the hidden state determines at which level of complexity the NN can grasp and link informations from the data. I tried a logarithmic approach, starting with 5, doubling each time the units. I found that with very low dimensions (5/10) the model could not learn adequately, while with higher dimensions (over 200) the model overfitted the data. I opted for 100 as final value for the dimension, as it was the best compromise between performance, size, which neither underfitted nor overfitted the dataset.
##### Adding dense layers after LTSM cells
I tried, while diminishing the dimension of the LTSM, to see if adding dense layers could in some ways better manipulate the data and compensate for the LTSM resizing. It was not surprising that, after overcoming all the problems with the vanishing gradient (the best function for the intermediate layers was the hard sigmoid), the model still could not learn. The relevant informations to decode the sequences are all in the previous signals, and it is then clear that the LTSM should be the most "heavy" part of the NN. 
##### Different sequence lengths
I tried to train the model with different input sequence length. Having always the same sequence length guaranteed to have always all the informations about the previous characters; during the training phase it resulted in a faster convergence rate and in a better final accuracy (96.25%, with stable loss function), while the model which allowed variable length only reached 90.11% accuracy. Even creating a larger dataset did not help. I figured out that the problem is when the sequence has length equal to 1 or equal to 2: the NN does not have sufficient information to classify the input. Setting a lower bound of 3 signals led to an accuracy of 94% with room for improvement (the loss function was still slightly decreasing after the 50th epoch). 
##### Drop rate
I played a bit with the drop rate in the LTSM layer, which should have helped to improve the performance when the model was overfitting. Surprisingly, even for low drop rates, the learning rate got really worse. I tried different combinations of drop and recurrent drop rates before realizing that it is actually useful that the model learns about feature coadaptation, since the signal type is correlated to the duration (if a signal is long, chances are it is a pause; if it is not, adequate countermeasures should be taken to manage the anomaly). From then the drop rates are always ground zero.
##### Other experiments
Besides playing a bit around with loss functions, learning rate decaying and dataset complexity there is no other relevant experimenting.

#### Final set of parameters
The final set of parameters is described above; it led to a final 96.25% accuracy, while the loss was almost stagnating. 
![Accuracy](/media/fixed_length_accuracy.png "Accuracy")
![Loss](/media/fixed_length_loss.png "Loss")
I could have ended the learning halfway, to save some time (the accuracy improved only by 1%). 

#### Testing
After choosing the hyperparameters, I tested the model and evaluated the results with the scorer:
| Indicator | Value |
|---|---|
|R^2| 0.9572839860884703|
|mean absolute error|0.03930000000000003|
|mean squared error |0.05609999999999999|
|root mean squared error| 0.2368543856465402|
|mean signed difference |-0.007899999999999992|
|mean absolute percentage error |0.018600000000000002|
|adjusted R^2 |0.9572839860884703|

These values indicates that the model classifies well the data of the dataset. 
I tried to manually put in the model a (voluntarily badly transmitted) message generated by the morseduino32, which said "ciao"; the model translated it with "c i a k", which tells me that I have a low inter-character speed and unstable speed even at letter level; this leads me to further improving the dataset generator, to better manage this extreme situations. 

I tried to input the whole fixed length dataset in the model trained on the varying length dataset, and its accuracy was af 94%; generating a completely different dataset (with different parameters for the functions) lead to a (expectably) lower accuracy of 91%. I will try to play with the parameters further to improve the adaptability of the model. 

### Next steps
I have successfully converted the keras model to a format uploadable on the morseduino; testing on the device and adjusting further the parameters will be the next steps.
