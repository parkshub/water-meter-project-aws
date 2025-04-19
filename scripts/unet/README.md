# Overview

This project is part of a bigger project. I'm building an app that helps visualize and extract water meter readings automatically. The idea is to let users upload an image of a water meter, have a model segment the meter region, and then run Tesseract to read the digits inside. Once the model is complete, this feature will be added to the AWS app [(Go to AWS deployment details)](../aws/README.md).

# Work in Progress

Currently, I'm training a U-NET model that uses grayscale images for segmentation. I'm exploring various loss functions to improve generalization. Although the biggest issue is generalization, I believe that by adding a dropout node and using image augmentation, I'll be able to improve validation loss.

Right now, the best results so far came from using:

    Learning rate: 0.0001

    Loss: Binary cross-entropy with class weighting (1.0 for background, 8.0 for foreground)

    Optimization: Adam

It does pretty well on the training set but falls apart on the test set. Validation loss is comparatively lower, so it's overfitting a bit. I'm currently trying out a combo loss function that combines BCE and Dice, a decaying learning rate, etc., to help with that.


## Model Architecture

<details>
<summary>Click to view full model summary</summary>

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
                                                                                                  
 ... (snip if too long for README) ...

 conv2d_19 (Conv2D)          (None, 512, 512, 1)          65        ['conv2d_18[0][0]']           
                                                                                                  
==================================================================================================
Total params: 31116161 (118.70 MB)
Trainable params: 31116161 (118.70 MB)
Non-trainable params: 0 (0.00 Byte)
__________________________________________________________________________________________________
```
</details>


## GIF of Progress
<!-- https://ezgif.com/maker -->
<details>
<summary>Click to view training GIF</summary>

![Model Training GIF](../../assets/learning.gif)

</details>