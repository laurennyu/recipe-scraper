# Supabase setup

1. Create a free project at https://supabase.com/dashboard/new. Pick the
   region nearest you and save the database password in a password manager.
2. In **SQL Editor**, create a new query, paste `schema.sql`, and run it.
3. In **Project Settings -> API**, copy the project URL and **service_role**
   key. The service-role key is a backend secret: do not put it in the Chrome
   extension or commit it to Git.
4. Copy the repository's `.env.example` to `.env` and add those two values.

The next application change will have the FastAPI server read those values and
use these tables instead of the local `recipes/` directory.
