# ProcessLine

Veri önişlemelerini middleware mantığıyla yapmanıza olanak tanır. Verilerinize yapılacak işlemlerinizi küçük fonksiyonlara bölerek yönetirsiniz. Şimdilik `CSV` ve `pickle` dosyaları işlemeyi desteklemektedir. Daha sonra  IO olarak dosya türünden bağımsız hatta TCP, http gibi haberleşme protokollerini de desteklemesi planlanmaktadır. Veriler akış (stream) mantığıyla işlendiği için tüm veri belleğe alınmayarak bellek verimli kullanılır.

## Temel Kullanım

`ProcessLine` klasörünüzü kendi projenize taşıdıktan sonra aşağıdaki gibi `Process` sınıfını kodunuza dahil ediniz.

```python
import ProcessLine.Process as pr

# Define IO
inp = pr.ProcessInput("input.csv", pr.ProcessIOType.Csv)
out = pr.ProcessOutput("output.pickle", pr.ProcessIOType.Pickle)

# Define process object
pro = pr.Process(inp, out)

# Specify middleware layers
pro.Layers = [
    # Here middleware functions will be specified.
]

# IO files are opening. 
pro.start()

# The process works here.
for row in pro.process():
    pass

# IO files are closing.
pro.close()
```

## Middleware Tanımlama

Middleware fonksiyon tanımlanırken fonksiyon minimum bir parametreli olur. İlk parametre bir önceki middleware fonksiyonundan gelen veriyi alabilmesi için kullanılır. `lyr` argümanı bir `generator` yapısıdır.  Fonksiyon içerisinde for döngüsü ile veriler tek tek okunur ve `return` yerine `yield` kullanılarak verilerin çıkışı sağlanır. 

```python
def TestLayer(lyr):
    for row in lyr:
        # Do preprocess for row.
        yield row
```

Bu katmanı `process` nesnemizin middleware listesi olan `pro.Layer` için ekleyelim.

```python
# Specify middleware layers
pro.Layers = [
    pr.Layer(TestLayer)
]
```



> **DİKKAT:** `yield`, `return` mekanizmasından farklı olarak fonksiyonu bitirmez. Bir sonraki veri için kaldığı yerden devam eder. Bu sebeple `yield` mekanizmasının altına kod yazarsanız bu kodların bir sonraki veri için çalışmaması için `continue` mekanizmasını kullanınız.