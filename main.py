# -*- coding: utf-8 -*-
"""main.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1--aYAu3D7EQy_YTEBj8WuhK2Pj7Zd8wx
"""

import os
import sys
os.add_dll_directory(r"C:\Users\rithe\miniconda3\envs\gpuenv\lib\site-packages\torch\lib")
import torch

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

import cv2

from sklearn.model_selection import train_test_split

import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator

from tensorflow.keras.applications import EfficientNetB0

from tensorflow.keras.applications import DenseNet121

# from tensorflow.keras.applications import ResNet50, preprocess_input

from tensorflow.keras.layers import Dense, GlobalAveragePooling2D

from tensorflow.keras.models import Model

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import recall_score

gpus = tf.config.list_physical_devices("GPU")
if gpus:
    for gpu in gpus:
        print("Found a GPU with the name:", gpu)
else:
    print("Failed to detect a GPU.")

positive_folder = 'Osteoporosis Positive Images'
negative_folder = 'Osteoporosis Negative Images'

dfn = pd.read_csv('osteopenia_nve.csv')
dfp = pd.read_csv('osteopenia_pve.csv')

dfn_copy = dfn.copy()
dfp_copy = dfp.copy()
dfn_copy['filestem'] = dfn_copy['filestem'].astype(str) + '.png'
dfp_copy['filestem'] = dfp_copy['filestem'].astype(str) + '.png'
dfn_copy['osteopenia'] = 0

# Function to load sample images
def load_sample_images(folder, filenames, num_samples):
    sample_images = []
    for filename in filenames[:num_samples]:
        img_path = os.path.join(folder, filename)
        img = cv2.imread(img_path)
        if img is not None:
            sample_images.append(img)
    return sample_images

# Load sample images from positive and negative classes
num_samples_per_class = 5

positive_sample_images = load_sample_images(positive_folder, dfp['filestem'].values, num_samples_per_class)
negative_sample_images = load_sample_images(negative_folder, dfn['filestem'].values, num_samples_per_class)

# Plot histogram showing the distribution of positive and negative samples
plt.figure(figsize=(10, 5))
plt.bar(['Positive', 'Negative'], [len(dfp), len(dfn)], color=['blue', 'red'])
plt.title('Distribution of Positive and Negative Samples')
plt.xlabel('Class')
plt.ylabel('Number of Samples')
plt.show()

# Plot sample images from positive class
if positive_sample_images:
    plt.figure(figsize=(15, 7))
    for i in range(min(num_samples_per_class, len(positive_sample_images))):
        plt.subplot(2, num_samples_per_class, i+1)
        plt.imshow(cv2.cvtColor(positive_sample_images[i], cv2.COLOR_BGR2RGB))
        plt.title('Positive Sample')
        plt.axis('off')

# Plot sample images from negative class
if negative_sample_images:
    plt.figure(figsize=(15, 7))
    for i in range(min(num_samples_per_class, len(negative_sample_images))):
        plt.subplot(2, num_samples_per_class, i+1)
        plt.imshow(cv2.cvtColor(negative_sample_images[i], cv2.COLOR_BGR2RGB))
        plt.title('Negative Sample')
        plt.axis('off')

plt.tight_layout()
plt.show()

positive_images = []
positive_filenames = []
for index, row in dfp_copy.iterrows():
    filename = row['filestem']
    img_path = os.path.join(positive_folder, filename)
    img = cv2.imread(img_path)
    if img is not None:
        positive_images.append(img)
        positive_filenames.append(filename)

negative_images = []
negative_filenames = []
for index, row in dfn_copy.iterrows():
    filename = row['filestem']
    img_path = os.path.join(negative_folder, filename)
    img = cv2.imread(img_path)
    if img is not None:
        negative_images.append(img)
        negative_filenames.append(filename)

plt.imshow(positive_images[0])
plt.axis('off')
plt.show()

len(positive_images)

len(negative_images)

import gc
gc.collect()

# Split positive images into train, validation, and test sets
X_positive_train, X_positive_temp, y_positive_train, y_positive_temp, positive_filenames_train, positive_filenames_temp = train_test_split(positive_images, dfp_copy['osteopenia'], positive_filenames, test_size=0.4, random_state=42, stratify=dfp_copy['osteopenia'])

X_positive_val, X_positive_test, y_positive_val, y_positive_test, positive_filenames_val, positive_filenames_test = train_test_split(X_positive_temp, y_positive_temp, positive_filenames_temp, test_size=0.5, random_state=42, stratify=y_positive_temp)

# Split negative images into train, validation, and test sets
X_negative_train, X_negative_temp, y_negative_train, y_negative_temp, negative_filenames_train, negative_filenames_temp = train_test_split(negative_images, dfn_copy['osteopenia'], negative_filenames, test_size=0.4, random_state=42, stratify=dfn_copy['osteopenia'])

X_negative_val, X_negative_test, y_negative_val, y_negative_test, negative_filenames_val, negative_filenames_test = train_test_split(X_negative_temp, y_negative_temp, negative_filenames_temp, test_size=0.5, random_state=42, stratify=y_negative_temp)

len(X_positive_train)

len(X_negative_test)

dfn_copy.to_csv('dfn_copy.csv')

X_positive_train[0].shape

#Augmentation parameters
augmentation_params = {
    'rotation_range': 20, # Rotate images by up to 20 degrees
    'width_shift_range': 0.1,  # Shift width by up to 10%
    'height_shift_range': 0.1,  # Shift height by up to 10%
    'horizontal_flip': True,  # Flip images horizontally
    'vertical_flip': False,  # Flip images vertically
    'brightness_range': [0.8, 1.2],  # Adjust brightness
    'zoom_range': 0.1,  # Zoom images by up to 10%
    'shear_range': 0.1  # Shear images by up to 10%
}

#ImageDataGenerator for augmentation
datagen = ImageDataGenerator(
    rotation_range=augmentation_params['rotation_range'],
    width_shift_range=augmentation_params['width_shift_range'],
    height_shift_range=augmentation_params['height_shift_range'],
    horizontal_flip=augmentation_params['horizontal_flip'],
    vertical_flip=augmentation_params['vertical_flip'],
    brightness_range=augmentation_params['brightness_range'],
    zoom_range=augmentation_params['zoom_range'],
    shear_range=augmentation_params['shear_range']
)

# Augment positive images with labels
X_positive_train_augmented = []
y_positive_train_augmented = []
positive_train_filenames_augmented = []  # New list for augmented file names

for img, label, filename in tqdm(zip(X_positive_train, y_positive_train, positive_filenames_train)):
    img_batch = img.reshape((1,) + img.shape)
    augmented_imgs = datagen.flow(img_batch, batch_size=1)
    original_index = len(X_positive_train_augmented)  # Store the index of the original image

    # Append original image
    X_positive_train_augmented.append(img)
    y_positive_train_augmented.append(label)
    positive_train_filenames_augmented.append(filename)  # Original filename

    # Generate and append augmented images
    for i in range(5):  # Augment each image 5 times
        augmented_img = next(augmented_imgs)[0].astype(np.uint8)  # Convert to np.uint8
        X_positive_train_augmented.append(augmented_img)
        y_positive_train_augmented.append(label)
        augmented_filename = f"{filename[:-4]}_{i+1}.png"  # Appending _(i+1) to the original filename
        positive_train_filenames_augmented.append(augmented_filename)
#678 iterations

gc.collect()

plt.imshow(X_positive_train_augmented[1])
plt.axis('off')
plt.show()
len(y_positive_train_augmented)

positive_train_filenames_augmented[1]

# # Augment positive images
# X_positive_train_augmented = []
# for img in tqdm(X_positive_train):
#     img_batch = img.reshape((1,) + img.shape)
#     augmented_imgs = datagen.flow(img_batch, batch_size=1)
#     augmented_images = [next(augmented_imgs)[0] for _ in range(5)]  # Augment each image 5 times
#     # Convert augmented images to np.uint8
#     augmented_images_uint8 = [np.uint8(image) for image in augmented_images]
#     X_positive_train_augmented.extend(augmented_images_uint8)

# # Assuming X_train is your array
# X_positive_train_augmented_array = np.array(X_positive_train_augmented)
# data_type = X_positive_train_augmented_array.dtype
# print("Data type of X_positive_train_augmented:", data_type)

index = 1  #Max index = 677 (length of X_positive_train)
num_augmented_images = 5  # Number of augmented images generated for each original image

plt.figure(figsize=(15, 5))

# Plot the original image
plt.subplot(1, num_augmented_images + 1, 1)
plt.imshow(X_positive_train_augmented[index * (num_augmented_images + 1)])  # Adjusted indexing
plt.title('Original')
plt.axis('off')

# Plot the augmented images
for i in range(num_augmented_images):
    plt.subplot(1, num_augmented_images + 1, i + 2)
    plt.imshow(X_positive_train_augmented[index * (num_augmented_images + 1) + i + 1])  # Adjusted indexing
    plt.title(f'Augmented {i+1}')
    plt.axis('off')

plt.show()

# Augment positive images with labels
X_positive_validation_augmented = []
y_positive_validation_augmented = []
positive_validation_filenames_augmented = []  # New list for augmented file names

for img, label, filename in tqdm(zip(X_positive_val, y_positive_val, positive_filenames_val)):
    img_batch = img.reshape((1,) + img.shape)
    augmented_imgs = datagen.flow(img_batch, batch_size=1)
    original_index = len(X_positive_validation_augmented)  # Store the index of the original image

    # Append original image
    X_positive_validation_augmented.append(img)
    y_positive_validation_augmented.append(label)
    positive_validation_filenames_augmented.append(filename)  # Original filename

    # Generate and append augmented images
    for i in range(5):  # Augment each image 5 times
        augmented_img = next(augmented_imgs)[0].astype(np.uint8)  # Convert to np.uint8
        X_positive_validation_augmented.append(augmented_img)
        y_positive_validation_augmented.append(label)
        augmented_filename = f"{filename[:-4]}_{i+1}.png"  # Appending _(i+1) to the original filename
        positive_validation_filenames_augmented.append(augmented_filename)
#226 iterations

plt.imshow(X_positive_validation_augmented[6])
plt.axis('off')
plt.show()
len(y_positive_validation_augmented)

positive_validation_filenames_augmented[6]

# # Assuming X_train is your array
# X_positive_validation_gmented_array = np.array(X_positive_validation_augmented)
# data_type = X_positive_train_augmented_array.dtype
# print("Data type of X_positive_validation_augmented:", data_type)

index = 1  #Max index = 226 (length of X_positive_val)
num_augmented_images = 5  # Number of augmented images generated for each original image

plt.figure(figsize=(15, 5))

# Plot the original image
plt.subplot(1, num_augmented_images + 1, 1)
plt.imshow(X_positive_validation_augmented[index * (num_augmented_images + 1)])  # Adjusted indexing
plt.title('Original')
plt.axis('off')

# Plot the augmented images
for i in range(num_augmented_images):
    plt.subplot(1, num_augmented_images + 1, i + 2)
    plt.imshow(X_positive_validation_augmented[index * (num_augmented_images + 1) + i + 1])  # Adjusted indexing
    plt.title(f'Augmented {i+1}')
    plt.axis('off')

plt.show()

# Augment positive images with labels
X_positive_testing_augmented = []
y_positive_testing_augmented = []
positive_testing_filenames_augmented = []  # New list for augmented file names

for img, label, filename in tqdm(zip(X_positive_test, y_positive_test, positive_filenames_test)):
    img_batch = img.reshape((1,) + img.shape)
    augmented_imgs = datagen.flow(img_batch, batch_size=1)
    original_index = len(X_positive_testing_augmented)  # Store the index of the original image

    # Append original image
    X_positive_testing_augmented.append(img)
    y_positive_testing_augmented.append(label)
    positive_testing_filenames_augmented.append(filename)  # Original filename

    # Generate and append augmented images
    for i in range(5):  # Augment each image 5 times
        augmented_img = next(augmented_imgs)[0].astype(np.uint8)  # Convert to np.uint8
        X_positive_testing_augmented.append(augmented_img)
        y_positive_testing_augmented.append(label)
        augmented_filename = f"{filename[:-4]}_{i+1}.png"  # Appending _(i+1) to the original filename
        positive_testing_filenames_augmented.append(augmented_filename)
#226 iterations

plt.imshow(X_positive_testing_augmented[6])
plt.axis('off')
plt.show()
len(y_positive_testing_augmented)

positive_testing_filenames_augmented[6]

index = 1  #Max index = 226 (length of X_positive_test)
num_augmented_images = 5  # Number of augmented images generated for each original image

plt.figure(figsize=(15, 5))

# Plot the original image
plt.subplot(1, num_augmented_images + 1, 1)
plt.imshow(X_positive_testing_augmented[index * (num_augmented_images + 1)])  # Adjusted indexing
plt.title('Original')
plt.axis('off')

# Plot the augmented images
for i in range(num_augmented_images):
    plt.subplot(1, num_augmented_images + 1, i + 2)
    plt.imshow(X_positive_testing_augmented[index * (num_augmented_images + 1) + i + 1])  # Adjusted indexing
    plt.title(f'Augmented {i+1}')
    plt.axis('off')

plt.show()

print('Original positive training images:', len(X_positive_train))
print('Augmented positive training images:', len(X_positive_train_augmented))
print('Original negative training images:', len(X_negative_train))
print()
print('Original positive validation images:', len(X_positive_val))
print('Augmented positive validation images:', len(X_positive_validation_augmented))
print('Original negative validation images:', len(X_negative_val))
print()
print('Original positive testing images:', len(X_positive_test))
print('Augmented positive testing images:', len(X_positive_testing_augmented))
print('Original negative testing images:', len(X_negative_test))

# # Augment negative images
# X_negative_train_augmented = []
# for img in tqdm(X_negative_train):
#     img_batch = img.reshape((1,) + img.shape)
#     augmented_imgs = datagen.flow(img_batch, batch_size=1)
#     X_negative_train_augmented.extend([next(augmented_imgs)[0] for _ in range(5)])  # Augment each image 5 times

# # Function to pad images to match the dimensions of the largest image
# def pad_images(images):
#     max_height = max(img.shape[0] for img in images)
#     max_width = max(img.shape[1] for img in images)
#     padded_images = []
#     for img in images:
#         pad_height = max_height - img.shape[0]
#         pad_width = max_width - img.shape[1]
#         pad_top = pad_height // 2
#         pad_bottom = pad_height - pad_top
#         pad_left = pad_width // 2
#         pad_right = pad_width - pad_left
#         padded_img = np.pad(img, ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)), mode='constant')
#         padded_images.append(padded_img)
#     return padded_images

# # Pad positive and negative training images
# X_positive_train_augmented_padded = pad_images(X_positive_train_augmented)
# X_positive_train_padded = pad_images(X_positive_train)
# X_negative_train_padded = pad_images(X_negative_train)

# # Concatenate padded positive and negative training images
# X_train_concatenated = np.concatenate((X_positive_train_augmented_padded, X_negative_train_padded))
# # Concatenate positive and negative training labels
# y_train_concatenated = np.concatenate((y_positive_train, y_negative_train))

# # Verify the shape of the concatenated arrays
# print("Shape of concatenated training images array:", X_train_concatenated.shape)
# print("Shape of concatenated training labels array:", y_train_concatenated.shape)

target_size = (255, 255)
# Resize images with specified interpolation method
X_positive_train_augmented_resized = [cv2.resize(img, target_size) for img in X_positive_train_augmented]
X_negative_train_resized = [cv2.resize(img, target_size) for img in X_negative_train]

# Now, you can concatenate the resized arrays
X_train = np.concatenate((X_positive_train_augmented_resized, X_negative_train_resized))
y_train = np.concatenate((y_positive_train_augmented, y_negative_train))
train_filenames = np.concatenate((positive_train_filenames_augmented, negative_filenames_train))

plt.imshow(X_train[7620])
plt.axis('off')
plt.show()
print(len(X_train))
print(len(y_train))

train_filenames[7620]

# Resize images for validation set
target_size = (255, 255)
X_positive_val_augmented_resized = [cv2.resize(img, target_size) for img in X_positive_validation_augmented]
X_negative_val_resized = [cv2.resize(img, target_size) for img in X_negative_val]

# Concatenate the resized arrays for validation set
X_val = np.concatenate((X_positive_val_augmented_resized, X_negative_val_resized))
y_val = np.concatenate((y_positive_validation_augmented, y_negative_val))
val_filenames = np.concatenate((positive_validation_filenames_augmented, negative_filenames_val))

plt.imshow(X_val[2540])
plt.axis('off')
plt.show()
print(len(X_val))
print(len(y_val))

val_filenames[2540]

# Resize images for testing set
target_size = (255, 255)
X_positive_test_augmented_resized = [cv2.resize(img, target_size) for img in X_positive_testing_augmented]
X_negative_test_resized = [cv2.resize(img, target_size) for img in X_negative_test]

# Concatenate the resized arrays for testing set
X_test = np.concatenate((X_positive_test_augmented_resized, X_negative_test_resized))
y_test = np.concatenate((y_positive_testing_augmented, y_negative_test))
test_filenames = np.concatenate((positive_testing_filenames_augmented, negative_filenames_test))

plt.imshow(X_test[123])
plt.axis('off')
plt.show()
print(len(X_test))
print(len(y_test))

test_filenames[123]

# def resize_and_pad(img, target_size):
#     resized_img = cv2.resize(img, target_size)
#     padded_img = np.zeros((target_size[1], target_size[1], 3), dtype=np.uint8)
#     padded_img[:resized_img.shape[1], :resized_img.shape[1], :] = resized_img
#     return padded_img

# X_positive_val_augmented_resized = [resize_and_pad(img, target_size) for img in X_positive_validation_augmented]
# X_negative_val_resized = [resize_and_pad(img, target_size) for img in X_negative_val]
# X_positive_val_resized = [resize_and_pad(img, target_size) for img in X_positive_val]

# # Normalize X_train to range [0, 1]
# X_train_normalized = X_train.astype('float32') / 255.0

# # Convert normalized X_train to uint8
# X_train_uint8 = (X_train_normalized * 255).astype('uint8')

# print("Before conversion:", X_train.dtype)
# X_train_uint8 = (X_train * 255).astype('uint8')
# print("After conversion:", X_train_uint8.dtype)

print("Minimum pixel value:", np.min(X_train))
print("Maximum pixel value:", np.max(X_train))

positive_images[134].shape

# Assuming X_train is your array
data_type = X_train.dtype
print("Data type of X_train:", data_type)

# Function to find the image with the largest dimensions
def find_largest_image(positive_images):
    largest_image_index = None
    largest_height = 0
    largest_width = 0

    for i, img in enumerate(positive_images):
        height, width, _ = img.shape
        if height > largest_height:
            largest_height = height
            largest_image_index = i
        if width > largest_width:
            largest_width = width

    return largest_image_index, largest_height, largest_width

# Function to find the image with the smallest dimensions
def find_smallest_image(positive_images):
    smallest_image_index = None
    smallest_height = float('inf')
    smallest_width = float('inf')

    for i, img in enumerate(positive_images):
        height, width, _ = img.shape
        if height < smallest_height:
            smallest_height = height
            smallest_image_index = i
        if width < smallest_width:
            smallest_width = width

    return smallest_image_index, smallest_height, smallest_width


largest_image_index, largest_height, largest_width = find_largest_image(positive_images)
smallest_image_index, smallest_height, smallest_width = find_smallest_image(positive_images)

print("Image with largest dimensions:")
print("Index:", largest_image_index)
print("Height:", largest_height)
print("Width:", largest_width)

print("\nImage with smallest dimensions:")
print("Index:", smallest_image_index)
print("Height:", smallest_height)
print("Width:", smallest_width)

def find_highest_height_image(positive_images):
    highest_height_index = None
    highest_height = 0

    for i, img in enumerate(positive_images):
        height, _, _ = img.shape
        if height > highest_height:
            highest_height = height
            highest_height_index = i

    return highest_height_index, highest_height

# Function to find the image with the highest width
def find_highest_width_image(positive_images):
    highest_width_index = None
    highest_width = 0

    for i, img in enumerate(positive_images):
        _, width, _ = img.shape
        if width > highest_width:
            highest_width = width
            highest_width_index = i

    return highest_width_index, highest_width

# Function to find the image with the lowest height
def find_lowest_height_image(positive_images):
    lowest_height_index = None
    lowest_height = float('inf')

    for i, img in enumerate(positive_images):
        height, _, _ = img.shape
        if height < lowest_height:
            lowest_height = height
            lowest_height_index = i

    return lowest_height_index, lowest_height

# Function to find the image with the lowest width
def find_lowest_width_image(positive_images):
    lowest_width_index = None
    lowest_width = float('inf')

    for i, img in enumerate(positive_images):
        _, width, _ = img.shape
        if width < lowest_width:
            lowest_width = width
            lowest_width_index = i

    return lowest_width_index, lowest_width


highest_height_index, highest_height = find_highest_height_image(positive_images)
highest_width_index, highest_width = find_highest_width_image(positive_images)
lowest_height_index, lowest_height = find_lowest_height_image(positive_images)
lowest_width_index, lowest_width = find_lowest_width_image(positive_images)

print("Image with highest height:")
print("Index:", highest_height_index)
print("Height:", highest_height)

print("\nImage with highest width:")
print("Index:", highest_width_index)
print("Width:", highest_width)

print("\nImage with lowest height:")
print("Index:", lowest_height_index)
print("Height:", lowest_height)

print("\nImage with lowest width:")
print("Index:", lowest_width_index)
print("Width:", lowest_width)

positive_images[657].shape

# Function to evaluate the model
def evaluate_model(model, X_test, y_test):
    # Make predictions on the test data
    y_pred = model.predict(X_test)
    # Convert predicted probabilities to binary predictions (0 or 1)
    y_pred_binary = (y_pred > 0.5).astype(int)
    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, y_pred_binary)
    precision = precision_score(y_test, y_pred_binary)
    recall = recall_score(y_test, y_pred_binary)
    f1 = f1_score(y_test, y_pred_binary)
    roc_auc = roc_auc_score(y_test, y_pred)
    return accuracy, precision, recall, f1, roc_auc

# Load pre-trained EfficientNet model
EfficientNet_base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(255, 255, 3))

# Add custom classification head
EfficientNet_x = GlobalAveragePooling2D()(EfficientNet_base_model.output)
EfficientNet_x = Dense(128, activation='relu')(EfficientNet_x)
EfficientNet_predictions = Dense(1, activation='sigmoid')(EfficientNet_x)

# Combine base model with custom head
EfficientNet_model = Model(inputs=EfficientNet_base_model.input, outputs=EfficientNet_predictions)

# Freeze base layers
for layer in EfficientNet_base_model.layers:
    layer.trainable = False

# Compile the model
EfficientNet_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
EfficientNet_history = EfficientNet_model.fit(X_train, y_train, batch_size=32, epochs=10, validation_data=(X_val, y_val))

# Optionally, fine-tune some layers
# for layer in model.layers[-20:]:
#     layer.trainable = True

# Compile the model again
# model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model again (fine-tuning)
# history = model.fit(X_train, y_train, batch_size=32, epochs=5, validation_data=(X_val, y_val))

# Evaluate the model
EfficientNet_test_loss, EfficientNet_test_acc = EfficientNet_model.evaluate(X_test, y_test)
print("EfficientNet Test Accuracy:", EfficientNet_test_acc)

# Evaluate the model
EfficientNet_accuracy, EfficientNet_precision, EfficientNet_recall, EfficientNet_f1, EfficientNet_roc_auc = evaluate_model(EfficientNet_model, X_test, y_test)

# Print the evaluation metrics
print("EfficientNet Evaluation Metrics:")
print(f"EfficientNet Accuracy: {EfficientNet_accuracy:.4f}")
print(f"EfficientNet Precision: {EfficientNet_precision:.4f}")
print(f"EfficientNet Recall: {EfficientNet_recall:.4f}")
print(f"EfficientNet F1-Score: {EfficientNet_f1:.4f}")
print(f"EfficientNet ROC-AUC: {EfficientNet_roc_auc:.4f}")

# Plot training and validation loss over epochs for each model
plt.figure(figsize=(5, 2))
plt.plot(EfficientNet_history.history['loss'], label='EfficientNet Training Loss')
plt.plot(EfficientNet_history.history['val_loss'], label='EfficientNet Validation Loss')
plt.title('EfficientNet Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()


# Plot training and validation accuracy over epochs for each model
plt.figure(figsize=(5, 2))
plt.plot(EfficientNet_history.history['accuracy'], label='EfficientNet Training Accuracy')
plt.plot(EfficientNet_history.history['val_accuracy'], label='EfficientNet Validation Accuracy')
plt.title('EfficientNet Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()


# Plot learning curves showing how the training and validation metrics change with the number of training examples
num_training_examples = np.arange(0, len(EfficientNet_history.history['loss']))

plt.figure(figsize=(5, 2))
plt.plot(num_training_examples, EfficientNet_history.history['loss'], label='EfficientNet Training Loss')
plt.plot(num_training_examples, EfficientNet_history.history['val_loss'], label='EfficientNet Validation Loss')
plt.title('EfficientNet Learning Curves')
plt.xlabel('Number of Training Examples')
plt.ylabel('Loss')
plt.legend()
plt.show()plt.figure(figsize=(5, 2))
plt.plot(num_training_examples, EfficientNet_history.history['accuracy'], label='EfficientNet Training Accuracy')
plt.plot(num_training_examples, EfficientNet_history.history['val_accuracy'], label='EfficientNet Validation Accuracy')
plt.title('EfficientNet Learning Curves')
plt.xlabel('Number of Training Examples')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Load pre-trained DenseNet model
DenseNet_base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(255, 255, 3))

# Add custom classification head
DenseNet_x = GlobalAveragePooling2D()(DenseNet_base_model.output)
DenseNet_x = Dense(128, activation='relu')(DenseNet_x)
DenseNet_predictions = Dense(1, activation='sigmoid')(DenseNet_x)

# Combine base model with custom head
DenseNet_model = Model(inputs=DenseNet_base_model.input, outputs=DenseNet_predictions)

# Freeze base layers
for layer in DenseNet_base_model.layers:
    layer.trainable = False

# Compile the model
DenseNet_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
DenseNet_history = DenseNet_model.fit(X_train, y_train, batch_size=32, epochs=10, validation_data=(X_val, y_val))

# Evaluate the model
DenseNet_test_loss, DenseNet_test_acc = DenseNet_model.evaluate(X_test, y_test)
print("DenseNet Test Accuracy:", DenseNet_test_acc)

# Evaluate the model
DenseNet_accuracy, DenseNet_precision, DenseNet_recall, DenseNet_f1, DenseNet_roc_auc = evaluate_model(DenseNet_model, X_test, y_test)

# Print the evaluation metrics
print("DenseNet Evaluation Metrics:")
print(f"DenseNet Accuracy: {DenseNet_accuracy:.4f}")
print(f"DenseNet Precision: {DenseNet_precision:.4f}")
print(f"DenseNet Recall: {DenseNet_recall:.4f}")
print(f"DenseNet F1-Score: {DenseNet_f1:.4f}")
print(f"DenseNet ROC-AUC: {DenseNet_roc_auc:.4f}")

plt.figure(figsize=(5, 2))
plt.plot(DenseNet_history.history['loss'], label='DenseNet Training Loss')
plt.plot(DenseNet_history.history['val_loss'], label='DenseNet Validation Loss')
plt.title('DenseNet Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()



plt.figure(figsize=(5, 2))
plt.plot(DenseNet_history.history['accuracy'], label='DenseNet Training Accuracy')
plt.plot(DenseNet_history.history['val_accuracy'], label='DenseNet Validation Accuracy')
plt.title('DenseNet Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()


plt.figure(figsize=(5, 2))
plt.plot(num_training_examples, DenseNet_history.history['loss'], label='DenseNet Training Loss')
plt.plot(num_training_examples, DenseNet_history.history['val_loss'], label='DenseNet Validation Loss')
plt.title('DenseNet Learning Curves')
plt.xlabel('Number of Training Examples')
plt.ylabel('Loss')
plt.legend()
plt.show()



plt.figure(figsize=(5, 2))
plt.plot(num_training_examples, DenseNet_history.history['accuracy'], label='DenseNet Training Accuracy')
plt.plot(num_training_examples, DenseNet_history.history['val_accuracy'], label='DenseNet Validation Accuracy')
plt.title('DenseNet Learning Curves')
plt.xlabel('Number of Training Examples')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Load pre-trained ResNeXt model
ResNeXt_base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(255, 255, 3))

# Add custom classification head
ResNeXt_x = GlobalAveragePooling2D()(ResNeXt_base_model.output)
ResNeXt_x = Dense(128, activation='relu')(ResNeXt_x)
ResNeXt_predictions = Dense(1, activation='sigmoid')(ResNeXt_x)

# Combine base model with custom head
ResNeXt_model = Model(inputs=ResNeXt_base_model.input, outputs=ResNeXt_predictions)

# Freeze base layers
for layer in ResNeXt_base_model.layers:
    layer.trainable = False

# Compile the model
ResNeXt_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
ResNeXt_history = ResNeXt_model.fit(X_train, y_train, batch_size=32, epochs=10, validation_data=(X_val, y_val))

# Evaluate the model
ResNeXt_test_loss, ResNeXt_test_acc = ResNeXt_model.evaluate(X_test, y_test)
print("ResNeXt Test Accuracy:", ResNeXt_test_acc)

# Evaluate the model
ResNeXt_accuracy, ResNeXt_precision, ResNeXt_recall, ResNeXt_f1, ResNeXt_roc_auc = evaluate_model(ResNeXt_model, X_test, y_test)

# Print the evaluation metrics
print("ResNeXt Evaluation Metrics:")
print(f"ResNeXt Accuracy: {ResNeXt_accuracy:.4f}")
print(f"ResNeXt Precision: {ResNeXt_precision:.4f}")
print(f"ResNeXt Recall: {ResNeXt_recall:.4f}")
print(f"ResNeXt F1-Score: {ResNeXt_f1:.4f}")
print(f"ResNeXt ROC-AUC: {ResNeXt_roc_auc:.4f}")