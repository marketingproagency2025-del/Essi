#!/usr/bin/env python3
"""Copy for the eight commercial service pages.

Every claim here traces to something the business already says about itself:
the services.html lead and description for each service, the matching ~1,300-word
guide, the "more than ten years of experience" line on index and about, the
"reply within one business day" line on contact, and the qualify-every-lead model
that the whole site rests on.

The Meta figures on the advertising page are the client's own, already published
on services.html, and verified against the source Ads Manager screenshot in
originals/ (28 May 2025): seven campaigns, 6,150 leads, 11,480.98 EUR spent.
Totals and the blended average are arithmetic on that table, nothing more.

NOT here, because the business has not supplied it: prices, delivery timelines,
deliverable counts, team size, founding year, tool names, client names. Each page
carries one marked slot where those go. See TODO_SLOT.
"""

# Shown on every page until the client supplies timelines and pricing. Deliberately
# one shared sentence rather than eight invented ones.
TODO_SLOT = (
    'Timelines and pricing depend on scope, so we quote per project rather than '
    'publishing a rate card. Tell us what you need and we will come back with a '
    'plan and a price. We usually reply within one business day, and often the '
    'same day.'
)

SERVICES = {
'services-social-media': dict(
    nav='Social Media', img='svc-social-1', guide='blog-social-media',
    guide_label='social media guide',
    title='Social Media Management Services | MarketingPro',
    desc='We run your social channels so followers turn into paying customers. Content, community, and every lead called and qualified before it reaches you.',
    h1='Social Media Management That Brings In Customers',
    alt='Refreshing summer cocktails styled for a social media post',
    service_name='Social Media Management', service_type='Social media management',
    lead=[
      'Most social media advice is about growing an audience. That is the easy part, and it is not the part that pays. A following that never becomes a customer is a cost centre with good engagement rates.',
      'We run social channels as a route to revenue rather than a scoreboard. That means content with a job to do, a presence on the platforms your buyers actually use, and a reply to every comment and message that could turn into work.',
    ],
    covers_h='What the service covers',
    covers=[
      'Planning and producing the content itself: what gets posted, in what order, and why each piece exists. Content with a purpose rather than content to fill a calendar.',
      'Choosing the channels worth your time. Being excellent on the two platforms your customers use beats being mediocre on six.',
      'Posting consistently, because sporadic brilliance loses to reliable presence every time.',
      'Community management. Comments and direct messages are where interest becomes an enquiry, and they are the part most businesses leave unattended.',
    ],
    how_h='How we work',
    how=[
      ('Find where your customers actually are', 'Not where the industry says they are. The platform choice comes from your buyers, not from what is fashionable.'),
      ('Give every post a job', 'Each piece of content is meant to do something specific: build trust, answer an objection, or ask for the sale. Content without a job is decoration.'),
      ('Show up on a schedule', 'Consistency is what compounds. It is also the thing most in-house efforts lose first when the week gets busy.'),
      ('Turn conversations into contracts', 'We work the comments and the inbox, and every lead that comes out of them is called and qualified by us before it reaches your sales team.'),
    ],
    who_h='Who this suits',
    who='Businesses whose customers are genuinely on social platforms and who are tired of measuring success in followers. It works best when there is something visual to show: a product, a space, a finished job.',
    faq=[
      ('Do more followers mean more customers?', 'Not by themselves. A large audience that never buys costs money to maintain. We optimise for enquiries and sales, and treat audience growth as a means rather than the goal.'),
      ('Which platforms will you use?', 'Whichever ones your customers are actually on. Most of our paid work runs on Meta, which covers Facebook and Instagram, but the organic channel mix is decided per client rather than by default.'),
      ('Do you handle the messages and comments too?', 'Yes. That is where interest turns into an enquiry, so it is part of the service rather than an add-on. Every lead that comes from it is called and qualified before we hand it over.'),
    ],
),
'services-advertising': dict(
    nav='Advertising', img='clients-1', guide='blog-advertising',
    guide_label='advertising guide',
    title='Meta and Google Ads Management | MarketingPro',
    desc='Targeted Meta and Google campaigns with every lead called and qualified before we hand it over. Seven campaigns, 6,150 leads, an average of 1.87 euro each.',
    h1='Ad Campaigns Where Every Lead Is Qualified',
    alt='Creative street advertising artwork',
    service_name='Advertising Campaigns', service_type='Advertising',
    lead=[
      'Anyone can spend money on ads. Making every euro come back with company is a different job, and it is where most budgets quietly leak.',
      'We run paid campaigns on Meta and Google, and then do the part almost nobody does: we call every lead ourselves, qualify it, and hand your team people who are ready to buy or ready for a quote. You are not buying traffic. You are buying conversations worth having.',
    ],
    covers_h='What the service covers',
    covers=[
      'Campaign strategy that starts from your commercial goal, not from a platform. The platform is a consequence of the goal, not the other way round.',
      'Meta and Google, chosen per client. They do two different jobs: one creates demand, the other captures it.',
      'Creative and audience testing, so decisions come from results rather than opinions.',
      'Retargeting the people who already showed interest, who are the warmest audience you will ever have and the cheapest to convert.',
      'The follow-up. Every lead is contacted and filtered by us before it reaches you.',
    ],
    how_h='How we work',
    how=[
      ('Start with the goal', 'Booked calls, quote requests, or sales. Everything downstream is chosen to serve that number.'),
      ('Pick the platform to match', 'Meta finds people who were not looking yet. Google catches people already searching. Most businesses need one more than the other.'),
      ('Test rather than guess', 'The same budget against the same audience can perform very differently depending on the creative. We find out which, rather than arguing about it.'),
      ('Retarget the warm audience', 'People who already engaged are the cheapest conversions available, and the easiest to leave on the table.'),
      ('Call and qualify every lead', 'This is the part that changes the economics. Your team stops spending its day on people who were never going to buy.'),
    ],
    proof_h='What that has looked like',
    proof=(
      'The Meta results published on our services page are real campaign exports, not illustrations. '
      'Across those seven campaigns: 6,150 leads from 1,084,529 people reached, at a blended cost of '
      '1.87 euro per lead, with individual campaigns landing between 1.47 and 2.30 euro. Total ad spend '
      'was 11,480.98 euro.'
    ),
    who_h='Who this suits',
    who='Businesses with something to sell now and a sales team, or an owner, who can follow up. If nobody can take the call, more leads will not help, and we would rather say so before you spend.',
    faq=[
      ('Which platforms do you advertise on?', 'Most of our paid campaigns run on Meta, meaning Facebook and Instagram, and on Google. Which one leads depends on whether your customers are already searching for what you sell.'),
      ('Do you really call every lead?', 'Yes. We generate the lead, then call and qualify it ourselves, so your team only speaks to people who are ready to buy or to ask for a quote. It is the reason our leads and other agencies leads are not the same thing.'),
      ('How quickly will I see results?', 'The first two weeks rarely reflect what the third month looks like. Early spend buys information as much as leads, and campaigns get cheaper per result as the testing narrows.'),
    ],
),
'services-website': dict(
    nav='Website', img='svc-web-1', guide='blog-website',
    guide_label='website guide',
    title='Website Design and Build | MarketingPro',
    desc='Websites built to turn visitors into enquiries, not just to look good. Fast, responsive, and structured so both search engines and buyers can find you.',
    h1='A Website That Sells, Not Just One That Looks Good',
    alt='A modern website builder interface',
    service_name='Website Creation', service_type='Web design',
    lead=[
      'A brochure describes what you do. A salesperson asks for the business. Most websites are brochures, which is why they get compliments and no enquiries.',
      'We build sites that guide a visitor toward getting in touch. That means fast loading, sensible structure, and every page having a job. It also means the site is built to be found, because a site nobody reaches is an expensive business card.',
    ],
    covers_h='What the service covers',
    covers=[
      'Design and build, on a structure planned around what you want visitors to do rather than around what looks good in a mockup.',
      'Speed. A site that takes too long loses people before they see anything, and search engines notice too.',
      'Mobile, properly. Most visitors arrive on a phone, so that is where the design has to work first.',
      'The technical groundwork that lets search engines understand and rank the site.',
      'Trust signals in the places where people hesitate.',
    ],
    how_h='What we build in',
    how=[
      ('A clear first five seconds', 'A visitor should know what you offer, who it is for, and why you, before they scroll.'),
      ('Speed as a feature', 'Not an optimisation done at the end. It affects both conversion and ranking.'),
      ('A job for every page', 'If a page does not know what it is asking the visitor to do, it will not get it.'),
      ('Built to be found', 'Structure, headings and markup that let search engines read the site properly from day one.'),
      ('Room to keep going', 'A website is never finished. The build is the start of the work, not the end of it.'),
    ],
    who_h='Who this suits',
    who='Businesses whose current site gets traffic but few enquiries, and businesses starting from nothing who would rather build it right once. If your site is fine and simply needs to be found, our SEO work may be the better first step.',
    faq=[
      ('Will the site work on phones?', 'Yes, and it is designed for phones first, because that is where most visitors arrive. Desktop is the second case, not the primary one.'),
      ('Can you improve the site I already have?', 'Often yes. If the foundations are sound it is usually faster and cheaper to fix structure, speed and conversion than to start again. We will tell you honestly which one your site needs.'),
      ('Do you handle the words as well as the design?', 'Yes. Design and copy are the same job on a page meant to convert; separating them is how sites end up looking good and saying nothing.'),
    ],
),
'services-seo': dict(
    nav='SEO', img='svc-seo-2', guide='blog-seo',
    guide_label='SEO guide',
    title='SEO Services for Italy, Europe and the US | MarketingPro',
    desc='SEO that lifts you up the results and keeps you there. Keyword research, content, technical fixes and authority, measured in enquiries not rankings.',
    h1='SEO That Keeps Working After You Stop Paying',
    alt='A search performance analytics dashboard',
    service_name='SEO', service_type='Search engine optimization',
    lead=[
      'A paid ad stops the moment you stop paying. A page that ranks keeps bringing in customers month after month. That is the appeal of SEO, and also why it asks for patience.',
      'We treat it as maintenance rather than magic. The results come from consistent work over months, they compound the longer you keep at it, and they fade if you stop. Most competitors give up early, and outlasting them is a large part of the job.',
    ],
    covers_h='What the service covers',
    covers=[
      'Finding what your customers actually type, which is rarely the phrasing you would use yourself.',
      'Content that answers the question behind the search rather than just containing the words.',
      'The technical foundations: speed, structure, markup, and everything that decides whether a page can rank at all.',
      'Authority earned rather than bought, because the bought kind is what ends in penalties.',
      'Local visibility where your customers search near them.',
    ],
    extra_h='AI search, also sold as AIO or AEO',
    extra=[
      'A share of buyers now ask an assistant before they open a search engine, and the answer names two or three suppliers rather than ten links. Nobody tells you when you were left out of one, which is why most owners have no idea it is happening.',
      'This is not a separate product and it is not sold here as one. The work overlaps almost entirely with the rest of this page: plain text under the heading that asks the question, a site whose meaning is not locked inside its pictures, and details that agree wherever a machine finds them. What changes is that we also read your site the way a machine reads it, and check what the assistants actually say about your trade before and after.',
      'Three acronyms are in circulation for it. AIO, AEO and GEO all describe the same job, so the one on a quote tells you when a supplier started offering this and nothing about how well they do it. And nobody can sell you a position inside an answer, because there is none to buy.',
    ],
    extra_link_lead='The longer version is here:',
    extra_guide='blog-ai-search',
    extra_guide_label='what an assistant says about your business',
    how_h='How we work',
    how=[
      ('Start with what people type', 'Keyword research, and just as importantly the intent behind each phrase. Someone asking what something costs and someone asking who provides it need two different pages.'),
      ('Write to answer, not to rank', 'Pages that satisfy the question outrank pages that repeat the keyword, and they keep doing it.'),
      ('Fix the foundations', 'Technical problems put a ceiling on everything else. They are unglamorous and they are usually where the fastest gains are.'),
      ('Earn authority', 'Relevant mentions and links, built slowly. Anything faster is the pitch that ends badly.'),
      ('Measure what matters', 'Enquiries and customers, not vanity positions on terms nobody buys from.'),
    ],
    who_h='Who this suits',
    who='Businesses willing to invest across months rather than weeks. If you need enquiries this month, paid advertising is the honest answer and we will say so. SEO is what makes those enquiries cheaper a year from now.',
    faq=[
      ('How long does SEO take to work?', 'The first few months are groundwork, real movement usually shows between months three and six, and the biggest compounding gains arrive after that. Anyone promising page one in a fortnight is best avoided.'),
      ('Is SEO better than paid ads?', 'They do different jobs. Ads buy visibility now and stop when the budget stops. SEO takes months and then keeps working. Most businesses need both, in that order.'),
      ('Do you guarantee first place?', 'No, and neither should anyone else. Nobody controls the ranking. What we control is the work that reliably moves sites up and keeps them there.'),
    ],
),
'services-sales-funnel': dict(
    nav='Sales Funnel', img='svc-funnel-1', guide='blog-sales-funnel',
    guide_label='sales funnel guide',
    title='Sales Funnel Design and Build | MarketingPro',
    desc='A mapped route from a stranger seeing your ad to a signed contract, with the leaks found and closed and every lead qualified before it reaches your team.',
    h1='A Funnel That Closes, Not Just One That Collects',
    alt='Two professionals celebrating a deal at a meeting',
    service_name='Sales Funnel', service_type='Sales funnel',
    lead=[
      'A brilliant lead is worth nothing without a path from interested to signed. Most businesses have the first step and the last step and nothing joining them, which is why good leads go cold.',
      'We map every stage from a stranger seeing your ad to a customer signing, then find the places people fall out and close them. It is a system rather than a lucky month.',
    ],
    covers_h='What the service covers',
    covers=[
      'The top of the funnel, where attention is earned and strangers first hear of you.',
      'The middle, where interest becomes trust and most funnels quietly fail.',
      'The bottom, where the decision is made easy rather than left to the buyer to figure out.',
      'Leak diagnosis. The money is usually hiding in the step nobody is watching.',
      'Follow-up, which is unglamorous, and which is the single highest-return part of the whole thing.',
    ],
    how_h='How we work',
    how=[
      ('Map what exists now', 'Before adding anything, we trace the route a real enquiry takes today, including the parts nobody designed.'),
      ('Find the leaks', 'A funnel rarely fails everywhere. It usually fails at one identifiable step, and fixing that beats rebuilding the whole thing.'),
      ('Build the middle', 'The stage between interest and decision is where most funnels have nothing at all.'),
      ('Make the decision easy', 'Remove the friction, the ambiguity and the unanswered objection at the point of commitment.'),
      ('Follow up properly', 'A lead is often only interested for a short window. Replying in minutes rather than days changes the outcome more than any other single change.'),
    ],
    who_h='Who this suits',
    who='Businesses already generating enquiries that are not converting. If leads arrive and go nowhere, the problem is usually the funnel rather than the traffic, and buying more traffic will simply cost more to waste.',
    faq=[
      ('What actually is a sales funnel?', 'The route someone takes from first hearing about you to becoming a customer. Every business already has one, whether or not anyone designed it. The question is only whether it works.'),
      ('Do I need one if my ads already work?', 'Especially then. Ads that produce leads a funnel cannot convert are the most expensive kind, because you are paying full price for a result you never collect.'),
      ('How fast does follow-up need to be?', 'Fast. Interest decays quickly, and replying in minutes rather than days changes the outcome more than almost anything else you could adjust.'),
    ],
),
'services-photo-video': dict(
    nav='Photo and Video', img='svc-photo-1', guide='blog-photo-video',
    guide_label='photo and video guide',
    title='Photo and Video Editing Services | MarketingPro',
    desc='Professional editing that makes your brand look its best. Colour, sound and consistency across every image and clip you put in front of a buyer.',
    h1='Editing That Makes Your Brand Look Its Best',
    alt='A photographer shooting a model in a red dress in a studio',
    service_name='Photo & Video Editing', service_type='Photo and video editing',
    lead=[
      'People judge a brand by how it looks, and they do it in a fraction of a second, before they have read a word. That judgement is made on your images whether or not you chose them carefully.',
      'Raw footage and unedited photographs are not ready. The gap between what the camera captured and what the buyer should see is the whole job, and it is the difference between looking like a business and looking like a hobby.',
    ],
    covers_h='What the service covers',
    covers=[
      'Photo editing: colour, light, correction and the small adjustments that make an image look deliberate.',
      'Video editing: cutting, pacing, colour and sound, which viewers forgive least of all.',
      'A consistent treatment across everything, because consistency is what turns a set of images into a brand.',
      'Formats and crops that suit where the work will actually be seen.',
    ],
    how_h='How we work',
    how=[
      ('Start from what you have', 'You do not need a production budget. Most businesses have more usable material than they think, badly presented.'),
      ('Fix what the eye notices', 'Exposure, colour and framing, so nothing looks accidental.'),
      ('Fix what the eye does not', 'Sound, pacing and the details people feel without being able to name. Bad audio reads as cheap faster than a bad picture does.'),
      ('Apply one consistent look', 'A recognisable treatment across every asset is what makes separate pieces read as one brand.'),
    ],
    who_h='Who this suits',
    who='Businesses with something physical to show: a product, a space, a finished installation. If you are already shooting content that is not landing, the editing is usually the gap rather than the camera.',
    faq=[
      ('Do I need professional footage to start?', 'No. Most businesses have more usable material than they realise. Good editing on decent phone footage beats bad editing on expensive footage more often than people expect.'),
      ('Can you match our existing brand look?', 'Yes. Consistency is the point of the exercise, so matching what you already have is usually the brief rather than an extra request.'),
      ('Is video really worth it over photos?', 'For attention, yes. Video holds people longer and is favoured almost everywhere it appears. That said, a consistent set of good photographs beats sporadic mediocre video.'),
    ],
),
'services-renders': dict(
    nav='Renders', img='svc-renders-1', guide='blog-renders',
    guide_label='guide to renders',
    title='3D Renders and Product Visualisation | MarketingPro',
    desc='Photorealistic 3D renders that let clients picture the finished result and say yes sooner, for products, spaces and concepts that do not exist yet.',
    h1='Sell the Vision Before It Is Built',
    alt='Architectural render of a whitewashed villa with a pool',
    service_name='Renders', service_type='3D rendering',
    lead=[
      'It is hard to sell something a client cannot see yet. Plans and drawings ask the buyer to do the imagining, and buyers who have to imagine tend to hesitate.',
      'A photorealistic render removes that doubt. It shows the finished thing in the real world, at the moment the decision is being made, which is exactly when hesitation costs the most.',
    ],
    covers_h='What the service covers',
    covers=[
      'Photorealistic visualisations of products, spaces and concepts.',
      'White background or a full contextual scene, depending on whether the job is a catalogue or a pitch.',
      'Product renders, including variants and finishes.',
      'Concept design, for the stage where the thing is still an argument rather than an object.',
      'The detail work that decides whether an image reads as real or as a drawing.',
    ],
    how_h='How we work',
    how=[
      ('Understand what has to be convincing', 'A render for a client meeting and a render for a catalogue are not the same image.'),
      ('Build it accurately', 'Photorealism is about trust. Materials and proportions that are almost right are what make a render feel wrong without the viewer knowing why.'),
      ('Show it in context', 'A product in a real setting sells better than the same product floating on white, because the buyer can place it.'),
      ('Change it before it is expensive', 'Adjustments at the render stage cost nothing compared with changes after manufacture or construction. Renders regularly catch mistakes that would have been expensive later.'),
      ('Reuse the output', 'A render is not just a decision aid. It becomes catalogue imagery, ad creative and website content.'),
    ],
    who_h='Who this suits',
    who='Anyone selling something before it exists: manufacturers, builders, interior and product designers. It is also for businesses whose product is real but impossible to photograph well in every configuration.',
    faq=[
      ('How is a render better than a photograph?', 'It exists before the product does, it can show every variant without building any of them, and it can place the item in a setting no photographer could stage.'),
      ('Can you show different finishes and options?', 'Yes, and that is often where renders pay for themselves. Once the model exists, additional variants cost far less than photographing physical alternatives.'),
      ('Can the renders be used for marketing too?', 'Yes. The same images work as catalogue photography, ad creative and website imagery, which is usually where most of the value ends up.'),
    ],
),
'services-catalogues': dict(
    nav='Catalogues', img='svc-catalog-2', guide='blog-catalogues',
    guide_label='catalogues guide',
    title='Catalogue Design, Print and Digital | MarketingPro',
    desc='Catalogues that sell rather than list. Concept, copywriting and design handled end to end, for print, digital or both, with room for every product.',
    h1='Catalogues That Sell, Not Spreadsheets With Pictures',
    alt='A design magazine with a single flower',
    service_name='Catalogues', service_type='Catalogue design',
    lead=[
      'A list informs. A story sells. Most catalogues are lists with photographs attached, which is why they get filed rather than read.',
      'A good catalogue is a salesperson on paper. It has an argument, a sequence, and a sense of what the reader should feel and do at each turn of the page. We handle it from the concept through the copywriting to the final design.',
    ],
    covers_h='What the service covers',
    covers=[
      'The creative concept, which decides what the catalogue is actually arguing before any page is laid out.',
      'Copywriting, because product names and dimensions are not persuasion.',
      'Design and layout, including how the eye is guided from page to page.',
      'Photography direction, which does more of the selling than any other element.',
      'Print, digital, or both, prepared properly for each.',
    ],
    how_h='How we work',
    how=[
      ('Decide what it is arguing', 'A catalogue with a point of view outsells a complete inventory, every time.'),
      ('Write it before designing it', 'Layout built around finished copy works. Copy poured into a finished layout does not.'),
      ('Let photography do the work', 'The images carry more of the persuasion than the words do, so they get decided early rather than sourced at the end.'),
      ('Guide the eye', 'Sequence and hierarchy decide what the reader sees first and what they do next.'),
      ('Prepare for where it lives', 'Print and digital want different things. A PDF of a print catalogue is not a digital catalogue.'),
    ],
    who_h='Who this suits',
    who='Businesses with a range worth presenting properly: manufacturers, wholesalers, and anyone whose buyers compare options side by side before deciding. It pairs naturally with renders when not every product can be photographed.',
    faq=[
      ('Print or digital?', 'It depends on how your buyers decide. Print still carries weight in a meeting and in a showroom; digital is easier to update and to send. Plenty of clients need both, prepared differently.'),
      ('Do you write the text as well?', 'Yes. Concept, copywriting and design are handled together, because a catalogue written after the layout is finished always reads like captions.'),
      ('What if we do not have good product photos?', 'That is common, and it is often where renders come in. A 3D render can present a product in configurations that would be impractical to photograph.'),
    ],
),
}
