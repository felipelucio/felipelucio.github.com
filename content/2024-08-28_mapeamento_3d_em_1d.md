---
title: Mapeamento de array 3D em 1D
date: 2024-08-28
category: dev
---

O "achatamento" de um array 3D em 1D é uma operação muito utilizada para a simplificação e otimização da alocação de memória, 
seja em linguagens como o C (na qual acho meio chato trabalhar com arrays com mais de uma dimensão), 
seja em linguagens como Python (na qual existe um *overhead* com a alocação de várias listas).

Apesar de relativamente simples, sempre que preciso utilizar tenho que gastar um tempo enorme buscando na internet ou em meus códigos antigos.

Por isso, resolvi deixar aqui os algoritmos que costumo utilizar na tranformação em ambos os sentidos. 

__IMPORTANTE__

Nos casos listados aqui, a ordem de crescimento do array é convencionada em X > Y > Z 
Ou seja, para um universo de tamanho 10x10x10:

```
Pos (x, y, z) | Índice
-------------------------
(0, 0, 0)     | 0
(1, 0, 0)     | 1
(0, 1, 0)     | 10
(0, 0, 1)     | 100
```

# De 3D para 1D
```python

# dimensões máximas dos eixos X, Y e Z
sizeX = 100
sizeY = 100
sizeZ = 100

# as coordenadas do ponto desejado
posX = 1
posY = 1
posZ = 1

index = (posZ * sizeY * sizeX) + (posY * sizeX) + posX

```


# De 1D para 3D
```python

# um índice qualquer
index = 12

# o calculo das coordenadas
posZ = math.floor(index / (sizeY * sizeX))
posY = math.floor((index - (posZ * sizeY * sizeX)) / sizeX)
posX = index % sizeX

```

# De 2D para 1D
```python

# dimensões máximas dos eixos X, Y
sizeX = 100
sizeY = 100

# as coordenadas do ponto desejado
posX = 1
posY = 1

index = (posY * sizeX) + posX

```

# De 1D para 2D
```python

# um índice qualquer
index = 12

# o calculo das coordenadas
posX = index % sizeX
posY = math.floor(index / sizeX)

```