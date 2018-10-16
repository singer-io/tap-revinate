# Revinate

## Connecting Revinate

### Revinate Setup Requirements

To set up Revinate in Stitch, you need access to the Revinate API and the following credentials:

-  **Username**: User's email address

-  **API Access Key**: provided by Revinate for User

-  **API Secret Key**: provided by Revinate for User

Reach out to your Revinate Account Manager for assistance. Once you receive this information, you can continue with the setup.

### Setup Revinate as a Stitch source

1. [Sign into your Stitch account](https://app.stitchdata.com/)

2. On the Stitch Dashboard page, click the **Add Integration** button.

3. Click the **Revinate** icon.

4. Enter a name for the integration. This is the name that will display on the Stitch Dashboard for the integration; it’ll also be used to create the schema in your destination. For example, the name "Stitch Revinate" would create a schema called `stitch_revinate` in the destination. **Note**: Schema names cannot be changed after you save the integration.

5. In the **Username** field, enter your Revinate username (email address). This user must have access to the Revinate API.

6. In the **API Key** field, enter your Revinate API Access Key.

7. In the **API Secret** field, enter your Revinate API Secret.

8. Accept the default **Start Date** (1 year of historical data), or select the **Start Date**. This date is the minimum, beginning date for Revinate Reviews (e.g. 2017-01-1).

---

## Revinate Replication

With each run of the integration, the following data sets are extracted and replicated to the data warehouse:

- **Hotels**: ALL Hotels will be replicated with each run.

- **Hotel Review Snapshots**: For ALL Hotels, the last completed weekly snapshot (Sunday to Sunday) will be replicate with each run.

- **Reviews**: Subset of new Reviews since the last_update (last completed run of the integeration). On the first run, ALL Reviews since the **Start Date** will be replicated.

---

## Revinate Table Schemas

### hotels

- Table name: hotel 
- Description: A list of ALL hotels and their addresses that are accessible to user's API key
- Primary key column: hotel_id
- Replicated fully
- Bookmark column: N/A
- API endpoint documentation: [hotels](https://porter.revinate.com/documentation#hotels)

### reviews

- Table name: review 
- Description: A subset of the latest reviews for the hotels accessible by the user's API key
- Primary key column: review_id
- Replicated incrementally
- Bookmark column: updated_at
- API endpoint documentation: [reviews](https://porter.revinate.com/documentation#reviews)

### hotel_reviews_snapshot

- Table name: hotel_reviews_snapshot 
- Description: Snapshot summary stats of reviews by hotel for the last completed week
- Primary key columns: hotel_id, snapshot_start_date
- Replicated partially (all hotels, last completed week only)
- Bookmark column: N/A
- API endpoint documentation: [hotel_reviews_snapshot](https://porter.revinate.com/documentation#hotels)

### hotel_reviews_snapshot_by_site

- Table name: hotel_reviews_snapshot_by_site 
- Description: Snapshot summary stats of reviews by hotel and review site for the last completed week
- Primary key columns: hotel_id, review_site_id, snapshot_start_date
- Replicated partially (all hotels and review sites, last completed week only)
- Bookmark column: N/A
- API endpoint documentation: [hotel_reviews_snapshot_by_site](https://porter.revinate.com/documentation#hotels)

### hotel_reviews_snapshot_by_time

- Table name: hotel_reviews_snapshot_by_time 
- Description: Snapshot summary stats of reviews by hotel for the last completed week
- Primary key columns: hotel_id, unix_time
- Replicated partially (all hotels, last completed week only)
- Bookmark column: N/A
- API endpoint documentation: [hotel_reviews_snapshot_by_site](https://porter.revinate.com/documentation#hotels)

---

## Troubleshooting / Other Important Info

- **Timestamps**: All timestamp columns and last_update state parameter are Unix timestamps.

- **JSON Elements**: The Revinate API returns JSON elements with nested structures. Depending on a client's Revinate subscriptions, a different subset of JSON elements may be provided. Many of the base JSON elements are flattened and parsed to columns in the data warehouse. A small subset were either not available during development and/or not parsed due to complexity. These JSON element structures are stored as text fields in the data warehouse.
