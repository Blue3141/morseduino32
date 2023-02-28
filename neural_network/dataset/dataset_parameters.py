# Parameters to generate the dataset

#--------------------------------------------------------------------------

## General parameters
FILE_NAME = 'dataset.csv'
DEBUG = True

#--------------------------------------------------------------------------

## Dataset parameters. A sample is the message from which sequences are
## generated
SEQ_NUMBER = 100000
SAMPLE_LENGTH = 100
SEQ_MAX_LENGTH = 10
ALWAYS_MAX_LENGTH = True
#--------------------------------------------------------------------------

## Speed of transmission parameters
SEQ_WPM_MIN = 5
SEQ_WPM_MAX = 20

#--------------------------------------------------------------------------

## Speed function parameters

# Generic speed parameters
F_SIN_N = 15
F_SIN_AMP_MEAN = 1
F_SIN_AMP_DEV = 25
F_SIN_PERIODS = [41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83,
                 89, 97, 101, 103, 107, 109, 113, 127, 131]

# Local speed parameters
F_SIN_L_N = 12
F_SIN_L_AMP_MEAN = 1
F_SIN_L_AMP_DEV = 7
F_SIN_L_PERIODS = [3, 5, 7, 9, 11, 13, 17, 19, 23,
                   29, 31, 37, 39]

#--------------------------------------------------------------------------

## Function noise parameters
NOISE_MEAN = 0
NOISE_DEV = 8

#--------------------------------------------------------------------------

## Morse text structure and composition parameters
MORSE_NEW_WORD_P = 0.18
MORSE_DIGITS_P = 0.10
MORSE_SYMBOLS_P = 0.05