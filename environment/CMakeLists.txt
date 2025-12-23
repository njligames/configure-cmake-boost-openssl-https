cmake_minimum_required(VERSION 3.16)
project(https_client LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Boost (Asio depends on boost::system)
find_package(Boost REQUIRED COMPONENTS system)

# OpenSSL (required for TLS)
find_package(OpenSSL REQUIRED)

add_executable(https_client
    main.cpp
)

target_include_directories(https_client PRIVATE
    ${Boost_INCLUDE_DIRS}
)

target_link_libraries(https_client PRIVATE
    Boost::system
    OpenSSL::SSL
    OpenSSL::Crypto
)
