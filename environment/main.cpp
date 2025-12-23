#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <iostream>
#include <string>

using boost::asio::ip::tcp;

int main() {
    try {
        // IO context and SSL context
        boost::asio::io_context io;
        boost::asio::ssl::context ctx(boost::asio::ssl::context::tls_client);

        // Configure TLS options
        ctx.set_default_verify_paths();
        ctx.set_options(
            boost::asio::ssl::context::default_workarounds |
            boost::asio::ssl::context::no_sslv2 |
            boost::asio::ssl::context::no_sslv3 |
            boost::asio::ssl::context::no_tlsv1 |
            boost::asio::ssl::context::no_tlsv1_1
        );

        // Create SSL socket
        boost::asio::ssl::stream<tcp::socket> socket(io, ctx);
        socket.set_verify_mode(boost::asio::ssl::verify_peer);
        socket.set_verify_callback(boost::asio::ssl::rfc2818_verification("example.com"));

        // Resolve host and connect
        tcp::resolver resolver(io);
        auto endpoints = resolver.resolve("example.com", "https");
        boost::asio::connect(socket.lowest_layer(), endpoints);

        // Perform SSL handshake
        socket.handshake(boost::asio::ssl::stream_base::client);

        // Send HTTP GET request
        std::string request =
            "GET / HTTP/1.1\r\n"
            "Host: example.com\r\n"
            "Connection: close\r\n\r\n";

        boost::asio::write(socket, boost::asio::buffer(request));

        // Read response status line
        boost::asio::streambuf response;
        boost::asio::read_until(socket, response, "\r\n");

        std::istream response_stream(&response);
        std::string http_version;
        unsigned int status_code;
        std::string status_message;

        response_stream >> http_version >> status_code;
        std::getline(response_stream, status_message);

        std::cout << "HTTP status code: " << status_code << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
