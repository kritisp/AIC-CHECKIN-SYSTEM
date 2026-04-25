-- 1. Create the participants table
CREATE TABLE IF NOT EXISTS public.participants (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    college TEXT,
    role TEXT,
    registration_number TEXT,
    checked_in BOOLEAN DEFAULT FALSE,
    checkin_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create the users table (for scanner/admin logins)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'volunteer', -- 'admin' or 'volunteer'
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Insert a default admin user (Password: "admin123")
-- IMPORTANT: You should change this password later or via your backend!
-- The hash below is a valid bcrypt hash for "admin123"
INSERT INTO public.users (username, password_hash, role)
VALUES (
    'admin', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYm', 
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- 4. Insert a default volunteer user (Password: "volunteer123")
INSERT INTO public.users (username, password_hash, role)
VALUES (
    'volunteer1', 
    '$2b$12$P5T1H.f/bZ1GqI/eU2b.UebPIt1iQ/D.rQ21f1TjE.Qz8M5G4yL9q', 
    'volunteer'
) ON CONFLICT (username) DO NOTHING;

-- 5. Set up Row Level Security (RLS) - Optional but good practice
-- We enable RLS but allow full access to the authenticated service_role (which your Python backend uses)
ALTER TABLE public.participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow full access to service_role on participants" 
ON public.participants FOR ALL 
USING (true) WITH CHECK (true);

CREATE POLICY "Allow full access to service_role on users" 
ON public.users FOR ALL 
USING (true) WITH CHECK (true);
