---
title: CMakeLists simples e direto
date: 2024-08-18
category: dev
---

Tenho uma dificuldade imensa em iniciar projetos no CMake. \
Sempre é um parto me entender com a DSL confusa dele. \
Pensando nisso, resolvi deixar esse CMakeLists simples para meu eu do futuro (boa sorte, camarada!).


# Disclaimer

Esse é um CMakeLists para iniciar um projeto de aplicação simples (ou seja, não serve para libs ou qualquer coisa para uso "público"). \
A ideia é usar ao máximo o sistema de download automático de dependências do próprio CMake (FetchContent). \
As definições de constantes são feitas no src/config.h.in \
Não gosto de usar o esquema de BLOB para adicionar os .c/.h de modo "automático". É só adicionar os arquivos desejados no add_executable.


# TODO

- Criar o script para empacotar as versões Release (copiar as pastas de resources, otimizações, etc.)


# O Código
```cmake
cmake_minimum_required(VERSION 3.27)
project(nome_do_projeto)

set(ENGINE_ROOT_DIR ${CMAKE_SOURCE_DIR})
configure_file(src/config.h.in src/config.h)
include_directories(${CMAKE_BINARY_DIR}/src)

add_executable(${PROJECT_NAME}
    src/main.c
)

# DEPENDENCIES
include(FetchContent)
find_package(OpenGL REQUIRED)

FetchContent_Declare(
        SDL2
        GIT_REPOSITORY https://github.com/libsdl-org/SDL.git
        GIT_TAG release-2.30.6
        GIT_SHALLOW TRUE
        GIT_PROGRESS TRUE
)
FetchContent_MakeAvailable(SDL2)

FetchContent_Declare(
    cglm
    GIT_REPOSITORY https://github.com/recp/cglm.git
    GIT_TAG v0.9.4
)
FetchContent_MakeAvailable(cglm)

target_link_libraries(${PROJECT_NAME} PRIVATE opengl32 cglm SDL2::SDL2main SDL2::SDL2)
```

