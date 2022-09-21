# DRAGN-Server
Code for the server to be run in the BYU DRAGN Lab

server.py - working HTTP server with basic pathing
client.py - working code on how to do a POST request to the server

For sending objects over Socket: https://stackoverflow.com/questions/47391774/python-send-and-receive-objects-through-sockets

Things to consider:

    CLIENT:
        - if the client limits where users can walk,
        there won't be problems of their location
        - client can independently load the map
        FUNCTIONS:
            - get_players() function that initializes
            server::send_players()

    SERVER:
        - server just keeps track of "sprites" where
        the players are.
        FUNCTIONS:
            - send_players() function that sends all
            current players to all connected clients.
