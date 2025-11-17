function BitstreamGenerator(bits)

%reads values from text file
binaryVals = readmatrix('imageMatrix.txt', 'OutputType', 'string');

%converts values to decimals
decVals = arrayfun(@bin2dec, binaryVals);

[rows, columns] = size(decVals);
bitstreams = strings(rows, columns);
selstreams = zeros(rows, columns);

for i = 1:rows
    for j = 1:columns
        prob = decVals(i,j) / 255;
        stream = "";
        rng(500);
        for k = 1:bits
            if(rand() <= prob)
                stream = stream + "1";
            else
                stream = stream + "0";
            end
        end
        bitstreams(i,j) = stream;
    end
end

for i = 1:rows
    for j = 1:columns
        rng(250);
        if(rand() <= 0.5)
            selstreams(i,j) = 1;
        else
            selstreams(i,j) = 0;
        end
    end
end

writematrix(bitstreams, 'bitstreams.txt');
writematrix(selstreams, 'selstreams.txt');
writematrix(decVals/255, 'imageMatrixDec.txt');

stochasticIntensities = zeros(rows, columns);

for i = 1:rows
    for j = 1:columns
        onesCount = 0;
        tempString = char(bitstreams(i,j));
        onesCount = sum(tempString == '1');
        value = onesCount / strlength(tempString);
        stochasticIntensities(i, j) = value;
    end
end

writematrix(stochasticIntensities, 'stochasticIntensities.txt');

end