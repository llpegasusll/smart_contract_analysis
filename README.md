# smart_contract_analysis
This code helps to label a non labelled dataset in MessiQ which has 40k verified smartcontracts 
Initial evaluation was done By running contract in Slither and SmartCheck
Slither identified the vulnerable contracts perfectly so it was used to label the dataset whic was used to train for ML algorithm 
SO it helps to label the dataset and helps to perform ML based activiteis this method an be further explored by naming each attack
sample 1 - had 2k contract sample 2 had 50 smart contract 

1. run Slither and Smartcehck script to run and identfy the vulnerable codes
2. run slither model script to create JSON of sample 1
3. run LSTM and CNN model script to train the model input is taken from above code t odo training sample 1
4. run Slither test script to  create JSON for sample 2
5. run LSTM and CNN prediction script to do prediction on sample 2
