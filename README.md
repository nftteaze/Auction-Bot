# Auct# Auction Bot

The Auction Bot is a feature-rich Discord bot designed to facilitate auctions for various products within a Discord server.

## Features

### Blind Bid Phase

During the blind bid phase, users can place bids for products without knowing the bids of others. Each user can bid on multiple products, and their bids remain hidden until the phase ends.

To participate in the blind bid phase, use the `/blindbid` command. The bot will prompt you to enter your AD Member number, bid amount, and the product number you want to bid on.

### Phase End

Admins can trigger the end of a phase for a specific product. The bot will then determine the successful bidders based on the highest bids for each product top 50%.

To end a phase for a specific product, admins can use the `/phaseend` command, followed by the product name. The bot will assign roles to successful bidders and create a private channel for them.

### Bid List

Users can view the bid list for a specific product to see who has the highest bid. The bid list displays the usernames, user IDs, and bid amounts for each bidder, sorted in descending order based on the bid amounts.

To view the bid list for a specific product, use the `/bidlist` command, followed by the product name.

### Clear Bids

Admins have the ability to clear bids for a specific user or all bids for a product. This feature is helpful if a user wants to retract their bid or if the auction requirements change during the blind bid phase.

To clear bids for a specific user, admins can use the `/bidclear` command, followed by the product name and the user mention.

To clear all bids for a specific product, admins can use the `/bidclearall` command, followed by the product name.

### Bid Export

Admins can export the bid list for a specific product as a text file. This is useful for record-keeping purposes or for sharing the results with other team members.

To export the bid list for a specific product, use the `/bidexport` command, followed by the product name. The bot will send the bid list as a downloadable text file.

## Prerequisites

- Python 3.8 or higher
- [disnake](https://github.com/EQUENOS/disnake) library

## Configuration

1. Create a new SQLite database and update the database connection string in the code.
   ```python
   conn = sqlite3.connect('bid_data.db')

How to Use the Bot
Invite the bot to your Discord server using the provided invite link.

Follow the commands and prompts provided by the bot to participate in the blind bid phase and manage the auction process.

Credits
This bot was created by NFTteaze.

License
This project is licensed under the MIT License.


I hope this detailed README provides a better understanding of the Auction Bot's capabilities. Feel free to customize the content further to reflect any additional features or information specific to your bot. If you have any more requests or questions, feel free to ask!
ion-Bot
