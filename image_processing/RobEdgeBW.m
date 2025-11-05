%performs Roberts Edge Detection to display a processed black and white image

function RobEdgeBW(img)

%converting image to matrix of intensities
A = imread(img);
AA = rgb2gray(A);
B = double(AA);

%displaying grayscale of original image
figure;
imshow(B/255);

%calculating the edges
C = edge(B, 'roberts');

%displaying the edges
figure;
imshow(uint8(C)*255);

end