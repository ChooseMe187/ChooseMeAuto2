# Mailchimp Setup & Automation Guide

This guide covers everything needed to set up Mailchimp integration, test it, and create email automations for Choose Me Auto.

---

## 1️⃣ Adding Mailchimp Credentials

### Step 1: Get Your Credentials from Mailchimp

**API Key:**
1. Log in to Mailchimp
2. Go to Account → Extras → API keys
3. Create a new key or copy existing one

**Server Prefix:**
- Look at your Mailchimp dashboard URL: `https://us21.admin.mailchimp.com`
- The `us21` part is your server prefix

**List ID (Audience ID):**
1. Go to Audience → Settings → Audience name and defaults
2. Find "Audience ID" at the bottom of the page

### Step 2: Add to Backend .env

Edit `/app/backend/.env` and add:

```bash
MAILCHIMP_API_KEY="your-key-here"
MAILCHIMP_SERVER_PREFIX="us21"  # or your server prefix
MAILCHIMP_LIST_ID="your-list-id"
```

### Step 3: Restart Backend

```bash
sudo supervisorctl restart backend
```

---

## 2️⃣ Testing Mailchimp Integration

### Submit a Test Lead

1. Go to your Pre-Approval page:
   ```
   https://your-site.com/preapproved
   ```

2. Submit a test lead:
   - **First Name**: Test
   - **Last Name**: Lead
   - **Phone**: 206-555-0000
   - **Email**: yourrealemail+pretest@gmail.com
   - **Stock Number**: (any vehicle from your inventory)

### Check Mailchimp Audience

1. Go to Mailchimp → Audience → All contacts
2. Look for the email you just submitted
3. It should show as "Subscribed"

### Verify Custom Fields

Check that the contact has:
- **FNAME**: Test
- **LNAME**: Lead
- **PHONE**: 206-555-0000
- **STOCK**: (the stock number you entered)
- **LEADTYPE**: preapproval
- **SOURCE**: preapproved-page

### Check Backend Logs

```bash
tail -f /var/log/supervisor/backend.out.log
```

Look for:
- `✅ Lead sent to Mailchimp successfully` (success)
- `❌ Mailchimp API error:` (if there's a problem)

---

## 3️⃣ Mailchimp Merge Fields Setup

Before automations work properly, create these custom fields in Mailchimp:

### How to Add Merge Fields

1. Go to Audience → All contacts
2. Click "Settings" → "Audience fields and *|MERGE|* tags"
3. Click "Add A Field"
4. Choose "Text" type and add these:

| Field Name | Tag | Type | Description |
|------------|-----|------|-------------|
| First Name | FNAME | Text | Built-in (already exists) |
| Last Name | LNAME | Text | Built-in (already exists) |
| Phone | PHONE | Phone | Customer phone number |
| Stock Number | STOCK | Text | Vehicle stock # they're interested in |
| Lead Type | LEADTYPE | Text | preapproval / test-drive / contact |
| Source | SOURCE | Text | Which page they came from |

---

## 4️⃣ Setting Up Email Automation

### Pre-Approval Follow-Up Email

#### Automation Setup in Mailchimp

1. Go to Automations → Create → Custom
2. **Trigger**: Contact joins audience
3. **Filter by**: LEADTYPE equals "preapproval"
4. **Timing**: Send immediately (0 minutes delay)

#### Email Template

**Subject Line Options:**
- ✅ "You're one step closer to driving with Choose Me Auto 🚗"
- ✅ "We got your info — now let's get you approved"
- ✅ "Bad credit? No problem. You're in the right place."

**Preview Text:**
```
We received your pre-approval request. Here's what happens next…
```

**From Name:** Choose Me Auto  
**From Email:** jay.alfred@choosemeauto.com

**Email Body:**

```
Hi *|FNAME|*,

Thanks for submitting your info through Choose Me Auto – you're officially one step closer to getting approved.

At Choose Me Auto, we specialize in helping:
• Bad credit
• No credit
• First-time buyers

We've received your request with the following details:

Name: *|FNAME|* *|LNAME|*
Phone: *|PHONE|*
Email: *|EMAIL|*
Vehicle / Stock #: *|STOCK|* (if provided)

✅ Step 1 – Complete the Secure Pre-Approval

To speed things up and get a real approval from the bank, please complete the secure pre-approval application at our partnered dealership:

👉 Finish your secure application here:
https://www.goodchev.com/preapproved.aspx

This helps us:
• Get you a real approval (not just a soft quote)
• See what banks and programs you qualify for
• Match you with the right vehicles and payment range

✅ Step 2 – We Go to Work for You

Once your application is submitted:
1. We review your approval with the lender
2. We match your approval to the best "payment-friendly" vehicles in stock
3. We reach out to confirm your budget, down payment, and appointment time

You'll hear from us by phone or text at *|PHONE|* or via this email.

📞 Questions or Prefer to Talk Now?

You can reach me directly:
• Call / Text: 206-786-1751
• Email: jay.alfred@choosemeauto.com

If anything on your credit has changed recently (new job, new address, recent payoff, etc.), reply to this email and let me know — it can actually help your approval.

🎯 Our Goal

We're here to make sure:
• You don't feel judged over your credit
• You don't waste time sitting for hours at the dealership
• You leave with a clear plan and vehicle options that actually fit your life

Thanks again for choosing Choose Me Auto to help you get approved the right way.

Talk soon,

Jay Alfred
Choose Me Auto
Call / Text: 206-786-1751
Email: jay.alfred@choosemeauto.com
```

---

## 5️⃣ Additional Automation Ideas

### Test Drive Follow-Up

**Trigger**: LEADTYPE equals "test-drive"  
**Timing**: Send immediately  
**Subject**: "Your Test Drive is Almost Scheduled 🚗"

**Key Points to Include:**
- Confirmation we received their test drive request
- Reminder to check their phone for our call/text
- Link to browse more vehicles while they wait
- Contact info if they want to expedite

### Contact Form Follow-Up

**Trigger**: LEADTYPE equals "contact"  
**Timing**: Send immediately  
**Subject**: "We Got Your Message - Here's What's Next"

**Key Points to Include:**
- Confirmation we received their message
- Expected response time (within 24 hours)
- Direct contact info if urgent
- Links to useful resources (inventory, pre-approval, FAQ)

### Abandoned Form Series

**Trigger**: Visited pre-approval page but didn't submit  
**Timing**: 1 hour, 1 day, 3 days  
**Subject**: "Still interested? We're here to help"

**Key Points to Include:**
- Reminder that approval is easier than they think
- Address common objections (bad credit, no down payment)
- Success stories or testimonials
- Easy next step with link back to form

---

## 6️⃣ Segmentation Strategies

### Create Segments for Targeted Campaigns

**High-Value Leads:**
- STOCK is not empty (they know what they want)
- Engaged with email (clicked links)

**Credit-Sensitive Leads:**
- Came from pre-approval page
- Haven't completed GoodChev application yet

**Shopping Leads:**
- LEADTYPE = "test-drive" or viewed multiple vehicles
- Haven't submitted pre-approval yet

**By Vehicle Type:**
- Filter by STOCK field to target leads interested in specific vehicles
- Send "similar vehicles" campaigns

---

## 7️⃣ Tracking & Optimization

### Key Metrics to Monitor

**Conversion Metrics:**
- Form submission → Email open rate
- Email open → Click-through rate
- Click-through → Completed application rate
- Overall: Website visit → Scheduled appointment

**Lead Quality:**
- Leads with stock number (shows intent)
- Leads with complete contact info
- Response time to calls/texts

### A/B Testing Ideas

**Subject Lines:**
- Test emotional vs. practical approaches
- Test with/without emojis
- Test urgency vs. helpfulness

**Email Content:**
- Test length (short vs. detailed)
- Test CTAs (button vs. text link)
- Test testimonials vs. benefits

**Timing:**
- Test immediate send vs. 15-minute delay
- Test business hours only vs. any time

---

## 8️⃣ Troubleshooting

### Lead Not Appearing in Mailchimp

**Check:**
1. Backend logs for Mailchimp errors
2. API key permissions in Mailchimp
3. List ID is correct
4. Email address format is valid

**Common Issues:**
- Email already exists in audience (won't add duplicate)
- API key doesn't have write permissions
- Server prefix doesn't match actual server
- List is archived or deleted

### Merge Fields Not Populating

**Check:**
1. Merge field tags match exactly (case-sensitive)
2. Custom fields exist in Mailchimp audience
3. Data is being sent from backend (check logs)

### Automations Not Triggering

**Check:**
1. Automation is turned ON
2. Filter conditions match exactly (LEADTYPE = "preapproval")
3. Tag or field exists in contact record
4. Contact isn't already in the automation journey

---

## 9️⃣ Best Practices

### Email Content

✅ **DO:**
- Keep mobile-friendly (60% read on phones)
- Use clear CTAs with buttons
- Personalize with merge tags
- Include contact info prominently
- Test all links before sending

❌ **DON'T:**
- Use too many images (hurts deliverability)
- Send from no-reply@ addresses
- Over-automate (max 3-4 emails per sequence)
- Forget unsubscribe link (required by law)

### List Hygiene

- Remove bounced emails monthly
- Archive unengaged contacts (no opens in 6 months)
- Honor unsubscribes immediately
- Segment active vs. inactive

### Compliance

- ✅ Include physical address in footer
- ✅ Clear unsubscribe link in every email
- ✅ Don't buy email lists
- ✅ Only email people who opted in (via your forms)

---

## 🎯 Summary Checklist

### Initial Setup
- [ ] Add Mailchimp credentials to .env
- [ ] Restart backend
- [ ] Create custom merge fields in Mailchimp
- [ ] Test with one lead submission
- [ ] Verify lead appears in Mailchimp
- [ ] Check all merge fields populated correctly

### Automation Setup
- [ ] Create pre-approval follow-up automation
- [ ] Create test drive follow-up automation
- [ ] Create contact form follow-up automation
- [ ] Test each automation with real submission
- [ ] Verify email content displays correctly
- [ ] Check links work in emails

### Ongoing Management
- [ ] Monitor open/click rates weekly
- [ ] A/B test subject lines monthly
- [ ] Clean list quarterly
- [ ] Update email content seasonally
- [ ] Review automation performance monthly

---

## 📞 Support Contacts

**Choose Me Auto:**
- Phone: (206) 786-1751
- Email: jay.alfred@choosemeauto.com

**Mailchimp Support:**
- Help Center: https://mailchimp.com/help/
- Email: support@mailchimp.com
- Phone: 1-800-315-5939

---

## 📝 Notes

- All three forms (Pre-Approval, Test Drive, Contact) already send to the same Mailchimp endpoint
- Leads are automatically tagged with LEADTYPE and SOURCE for segmentation
- System is production-ready once credentials are added
- No code changes needed - just add credentials and restart backend
