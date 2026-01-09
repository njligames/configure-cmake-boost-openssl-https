cat <<'EOF' > main.cpp
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <openssl/ssl.h>

#include <iostream>
#include <string>
#include <cstdlib>

namespace asio = boost::asio;
using tcp = asio::ip::tcp;

static void fail(const std::string& where, const std::string& message) {
    std::cerr << "[ERROR] " << where << ": " << message << std::endl;
}

int main() {
    try {
        asio::io_context io;

        // ---- SSL context ----
        asio::ssl::context ctx(asio::ssl::context::tls_client);

        boost::system::error_code ec;
        ctx.set_default_verify_paths(ec);
        if (ec) {
            fail("SSL context", "failed to load default verify paths: " + ec.message());
            return EXIT_FAILURE;
        }

        ctx.set_verify_mode(asio::ssl::verify_peer);

        asio::ssl::stream<tcp::socket> socket(io, ctx);

        // ---- DNS resolution ----
        tcp::resolver resolver(io);
        auto endpoints = resolver.resolve("example.com", "443", ec);
        if (ec || endpoints.empty()) {
            fail("DNS resolution", ec ? ec.message() : "no endpoints returned");
            return EXIT_FAILURE;
        }

        // ---- TCP connect ----
        asio::connect(socket.lowest_layer(), endpoints, ec);
        if (ec) {
            fail("TCP connect", ec.message());
            return EXIT_FAILURE;
        }

        // ---- SNI (MANDATORY) ----
        if (!SSL_set_tlsext_host_name(socket.native_handle(), "example.com")) {
            fail("TLS setup", "failed to set SNI hostname");
            return EXIT_FAILURE;
        }

        // ---- TLS handshake ----
        socket.handshake(asio::ssl::stream_base::client, ec);
        if (ec) {
            fail("TLS handshake", ec.message());
            return EXIT_FAILURE;
        }

        // ---- HTTP request ----
        const std::string request =
            "GET / HTTP/1.1\r\n"
            "Host: example.com\r\n"
            "Connection: close\r\n\r\n";

        asio::write(socket, asio::buffer(request), ec);
        if (ec) {
            fail("HTTP write", ec.message());
            return EXIT_FAILURE;
        }

        // ---- Read HTTP status line ----
        asio::streambuf response;
        asio::read_until(socket, response, "\r\n", ec);
        if (ec) {
            fail("HTTP read", ec.message());
            return EXIT_FAILURE;
        }

        std::istream response_stream(&response);

        std::string http_version;
        unsigned int status_code = 0;

        response_stream >> http_version >> status_code;

        if (!response_stream || http_version.rfind("HTTP/", 0) != 0) {
            fail("HTTP parse", "invalid HTTP status line");
            return EXIT_FAILURE;
        }

        if (status_code < 100 || status_code > 599) {
            fail("HTTP parse", "invalid HTTP status code");
            return EXIT_FAILURE;
        }

        // ---- Success ----
        std::cout << status_code << std::endl;
        return EXIT_SUCCESS;

    } catch (const std::exception& e) {
        fail("Unhandled exception", e.what());
        return EXIT_FAILURE;
    } catch (...) {
        fail("Unhandled exception", "unknown error");
        return EXIT_FAILURE;
    }
}

EOF

cat <<'EOF' > CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(https_client LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Boost REQUIRED COMPONENTS system)
find_package(OpenSSL REQUIRED)

add_executable(main main.cpp)

target_link_libraries(main
    PRIVATE
        Boost::system
        OpenSSL::SSL
        OpenSSL::Crypto
)

EOF
