import csv
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Flatten, Dense, Lambda, Dropout
from keras.layers.convolutional import Convolution2D, Cropping2D
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from keras.utils import plot_model




def generator(samples, batch_size=32):
    num_samples = len(samples)
    while 1:    #loop forever so the generator never terminates
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]
            images = []
            measurements = []
            correction = 0.2 # this is a parameter to tune
            for line in batch_samples:
                # read the middle, left, right images
                image_center = plt.imread('../data/' + line[0])
                image_left = plt.imread('../data/IMG/' + line[1].split('/')[-1])
                image_right = plt.imread('../data/IMG/' + line[2].split('/')[-1])
                images.extend([image_center, image_left, image_right])
                # read steering angles
                steering_center = float(line[3])
                steering_left = steering_center + correction # 0.4
                steering_right = steering_center - correction # 0.3
                measurements.extend([steering_center, steering_left, steering_right])
                # flip to augmentation data
#                images.extend([np.fliplr(image_center), np.fliplr(image_left), np.fliplr(image_right)])
#                measurements.extend([-steering_center, -steering_left, -steering_right])
                images.append(np.fliplr(image_center))
                measurements.append(-steering_center)
                              
            X_train = np.array(images)
            y_train = np.array(measurements)         
            yield shuffle(X_train, y_train)



samples = []
# Open the csv log file and read the file name of the figure
with open('../data/driving_log.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None) # skip the headers
    for line in reader:
        samples.append(line)       
# divide into train and validation 
train_samples, validation_samples = train_test_split(samples, test_size=0.2)
train_generator = generator(train_samples)
validation_generator = generator(validation_samples)

# Nvidia End to End Self-driving Car CNN
model = Sequential()
model.add(Cropping2D(cropping=((70,25), (0,0)), input_shape=(160, 320, 3))) # crop interested area
model.add(Lambda(lambda x: x / 127.5 - 1.)) # Normalize

model.add(Convolution2D(24,5,5, subsample=(2,2), activation='relu'))
#model.add(Convolution2D(36,5,5, subsample=(2,2), activation='relu'))
#model.add(Convolution2D(48,5,5, subsample=(2,2), activation='relu'))
#model.add(Convolution2D(64,3,3, activation='relu'))
#model.add(Convolution2D(64,3,3, activation='relu'))

model.add(Flatten())
model.add(Dropout(0.3)) # prevent overfit

#model.add(Dense(100))
#model.add(Dense(50))
#model.add(Dropout(0.2))
#model.add(Dense(10))
model.add(Dense(1))
print('model ready')

model.compile(loss='mse', optimizer='adam')
history_object = model.fit_generator(
        generator = train_generator, samples_per_epoch = len(train_samples),
        validation_data = validation_generator, nb_val_samples = len(validation_samples),
        nb_epoch=10, verbose=1)

model.save('model.h5')










plot_model(model, to_file='model.png')
print('save model')

# print the keys contained in the history object
print(history_object.history.keys())

# plot the training and validation loss for each epoch
plt.plot(history_object.history['loss'])
plt.plot(history_object.history['val_loss'])
plt.title('model mean squared error loss')
plt.ylabel('mean squared error loss')
plt.xlabel('epoch')
plt.legend(['training set', 'validation set'], loc='upper right')
plt.show()
plt.savefig('loss_curve.jpg')

# Plot training & validation accuracy values
plt.plot(history_object.history['acc'])
plt.plot(history_object.history['val_acc'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()
plt.savefig('accuracy_curve.jpg')


