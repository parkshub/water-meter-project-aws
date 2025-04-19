# Overview

This project is part of a bigger project. I'm building an app that helps visualize and extract water meter readings automatically. The idea is to let users upload an image of a water meter, have a model segment the meter region, and then run Tesseract to read the digits inside. Once the model is complete, this feature will be added to the AWS app [(Go to AWS deployment details)](../aws/README.md).

# Work in Progress

Currently, I'm training a U-NET model that uses grayscale images for segmentation. I'm exploring various loss functions to improve generalization. Although the biggest issue is generalization, I believe that by adding a dropout node and using image augmentation, I'll be able to improve validation loss.

Right now, the best results so far came from using:

    Learning rate: 0.0001

    Loss: Binary cross-entropy with class weighting (1.0 for background, 8.0 for foreground)

    Optimization: Adam

It does pretty well on the training set but falls apart on the test set. Validation loss is comparatively lower, so it's overfitting a bit. I'm currently trying out a combo loss function that combines BCE and Dice, a decaying learning rate, etc., to help with that.

## GIF of Progress
<!-- https://ezgif.com/maker -->
<!-- <details> -->
<!-- <summary>Click to view training GIF</summary> -->

![Model Training GIF](../../assets/learning.gif)

<!-- </details> -->


## Model Architecture

<!-- <details> -->
<!-- <summary>Click to view full model summary</summary> -->

```txt
__________________________________________________________________________________________________
 Layer (type)                Output Shape                 Param #   Connected to                  
==================================================================================================
 input_1 (InputLayer)        [(None, 512, 512, 1)]        0         []                            
                                                                                                  
 conv2d (Conv2D)             (None, 512, 512, 64)         640       ['input_1[0][0]']             
                                                                                                  
 conv2d_1 (Conv2D)           (None, 512, 512, 64)         36928     ['conv2d[0][0]']              
                                                                                                  
 max_pooling2d (MaxPooling2  (None, 256, 256, 64)         0         ['conv2d_1[0][0]']            
 D)                                                                                               
                                                                                                  
 conv2d_2 (Conv2D)           (None, 256, 256, 128)        73856     ['max_pooling2d[0][0]']       
                                                                                                  
 conv2d_3 (Conv2D)           (None, 256, 256, 128)        147584    ['conv2d_2[0][0]']            
                                                                                                  
 max_pooling2d_1 (MaxPoolin  (None, 128, 128, 128)        0         ['conv2d_3[0][0]']            
 g2D)                                                                                             
                                                                                                  
 conv2d_4 (Conv2D)           (None, 128, 128, 256)        295168    ['max_pooling2d_1[0][0]']     
                                                                                                  
 conv2d_5 (Conv2D)           (None, 128, 128, 256)        590080    ['conv2d_4[0][0]']            
                                                                                                  
 max_pooling2d_2 (MaxPoolin  (None, 64, 64, 256)          0         ['conv2d_5[0][0]']            
 g2D)                                                                                             
                                                                                                  
 conv2d_6 (Conv2D)           (None, 64, 64, 512)          1180160   ['max_pooling2d_2[0][0]']     
                                                                                                  
 conv2d_7 (Conv2D)           (None, 64, 64, 512)          2359808   ['conv2d_6[0][0]']            
                                                                                                  
 max_pooling2d_3 (MaxPoolin  (None, 32, 32, 512)          0         ['conv2d_7[0][0]']            
 g2D)                                                                                             
                                                                                                  
 conv2d_8 (Conv2D)           (None, 32, 32, 1024)         4719616   ['max_pooling2d_3[0][0]']     
                                                                                                  
 conv2d_9 (Conv2D)           (None, 32, 32, 1024)         9438208   ['conv2d_8[0][0]']            
                                                                                                  
 up_sampling2d (UpSampling2  (None, 64, 64, 1024)         0         ['conv2d_9[0][0]']            
 D)                                                                                               
                                                                                                  
 conv2d_10 (Conv2D)          (None, 64, 64, 512)          2097664   ['up_sampling2d[0][0]']       
                                                                                                  
 concatenate (Concatenate)   (None, 64, 64, 1024)         0         ['conv2d_10[0][0]',           
                                                                     'conv2d_7[0][0]']            
                                                                                                  
 conv2d_11 (Conv2D)          (None, 64, 64, 512)          4719104   ['concatenate[0][0]']         
                                                                                                  
 conv2d_12 (Conv2D)          (None, 64, 64, 512)          2359808   ['conv2d_11[0][0]']           
                                                                                                  
 up_sampling2d_1 (UpSamplin  (None, 128, 128, 512)        0         ['conv2d_12[0][0]']           
 g2D)                                                                                             
                                                                                                  
 concatenate_1 (Concatenate  (None, 128, 128, 768)        0         ['up_sampling2d_1[0][0]',     
 )                                                                   'conv2d_5[0][0]']            
                                                                                                  
 conv2d_13 (Conv2D)          (None, 128, 128, 256)        1769728   ['concatenate_1[0][0]']       
                                                                                                  
 conv2d_14 (Conv2D)          (None, 128, 128, 256)        590080    ['conv2d_13[0][0]']           
                                                                                                  
 up_sampling2d_2 (UpSamplin  (None, 256, 256, 256)        0         ['conv2d_14[0][0]']           
 g2D)                                                                                             
                                                                                                  
 concatenate_2 (Concatenate  (None, 256, 256, 384)        0         ['up_sampling2d_2[0][0]',     
 )                                                                   'conv2d_3[0][0]']            
                                                                                                  
 conv2d_15 (Conv2D)          (None, 256, 256, 128)        442496    ['concatenate_2[0][0]']       
                                                                                                  
 conv2d_16 (Conv2D)          (None, 256, 256, 128)        147584    ['conv2d_15[0][0]']           
                                                                                                  
 up_sampling2d_3 (UpSamplin  (None, 512, 512, 128)        0         ['conv2d_16[0][0]']           
 g2D)                                                                                             
                                                                                                  
 concatenate_3 (Concatenate  (None, 512, 512, 192)        0         ['up_sampling2d_3[0][0]',     
 )                                                                   'conv2d_1[0][0]']            
                                                                                                  
 conv2d_17 (Conv2D)          (None, 512, 512, 64)         110656    ['concatenate_3[0][0]']       
                                                                                                  
 conv2d_18 (Conv2D)          (None, 512, 512, 64)         36928     ['conv2d_17[0][0]']           
                                                                                                  
 conv2d_19 (Conv2D)          (None, 512, 512, 1)          65        ['conv2d_18[0][0]']           
                                                                                                  
==================================================================================================
Total params: 31116161 (118.70 MB)
Trainable params: 31116161 (118.70 MB)
Non-trainable params: 0 (0.00 Byte)
__________________________________________________________________________________________________
```
<!-- </details> -->