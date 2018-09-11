# tap-revinate

Author: Jeff Huth (jeff.huth@bytecode.io)

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:
- Pulls raw data from the [Revinate Porter API](https://porter.revinate.com/documentation)
- Extracts the following resources:
  - Hotels
  - Reviews
  - Hotel Review Snapshot
- Outputs the schema for each resource
- Incrementally pulls data based on the input state (for Reviews only)


## Quick start

1. Install

    ```bash
    > git clone git@github.com:singer-io/tap-revinate.git
    > cd tap-revinate
    > pip install .
    ```

2. Get credentials from Revinate:

    You'll need:

    - A Revinate username (email address) with access to the API
    - A Revinate API key and secret (your account manager can give you these)

3. Create the config file.

    There is a template you can use at `config.json.example`, just copy it to `config.json`
    in the repo root and insert your credentials.

    - `username`, your Revinate username (email address) 
    - `api_key`, your Revinate API key (from your account manager)
    - `api_secret`, your Revinate API secret (from your account manager)
    - `start_date`, the date from which you want to sync data, in the format `2018-08-01`

4. Run the application.

   ```bash
   tap-revinate --config config.json
   ```

   Or:
   ```bash
   tap-revinate -c ./tap-revinate/config.json | target-csv
   ```

   Or:
   ```bash
   tap-revinate --config ./tap-revinate/config.json --state ./tap-revinate/state.json | target-csv
   ```

   Or: 
   ```bash
   tap-revinate --config ./tap-revinate/config.json --state ./tap-revinate/state.json | singer-check-tap
   ```
---

Copyright &copy; 2018 Stitch
