# Configuration System

This directory contains the centralized configuration system for QCanvas. All project details, team information, and shared constants are managed through this system to ensure consistency across the application.

## Files

### `config.ts`
The main configuration file containing all project settings, team information, and shared constants.

## Usage

Import the configuration in any component:

```typescript
import { config } from '@/lib/config'

// Access project information
const projectName = config.project.name
const teamMembers = config.team
const socialLinks = config.social

// Use helper functions
import { getCopyrightText, getTeamMemberByName } from '@/lib/config'
const copyright = getCopyrightText()
const member = getTeamMemberByName('Umer Farooq')
```

## Configuration Sections

### Project Information (`config.project`)
- `name`: Project name
- `tagline`: Short project description
- `description`: Full project description
- `year`: Project year
- `version`: Current version
- `status`: Development stage

### Team Information (`config.team`)
Array of team members with:
- `name`: Full name
- `role`: Job title/role
- `profile`: Student ID or profile identifier
- `github`: GitHub profile URL
- `linkedin`: LinkedIn profile URL
- `email`: Contact email

### Social Links (`config.social`)
- `github`: Main project repository
- `discord`: Community Discord server
- `twitter`: Twitter account
- `linkedin`: LinkedIn page

### Contact Information (`config.contact`)
- `email`: General contact email
- `support`: Support email
- `research`: Research contact
- `community`: Community contact

### Technical Specifications (`config.technical`)
- `frameworks`: Supported quantum frameworks
- `standards`: Supported standards
- `features`: Key features

### Navigation (`config.navigation`)
Menu items for navigation:
- `name`: Display name
- `path`: Route path
- `icon`: Icon identifier

### Footer Links (`config.footer`)
Structured footer links:
- `platform`: Main platform pages
- `community`: Social and community links
- `support`: Support and contact links

## Helper Functions

### `getTeamMemberByName(name: string)`
Finds a team member by their full name.

### `getTeamMemberByProfile(profile: string)`
Finds a team member by their profile identifier.

### `getFullProjectTitle()`
Returns formatted project title.

### `getProjectDescription()`
Returns formatted project description with team credits.

### `getCopyrightText()`
Returns formatted copyright notice.

### `getVersionText()`
Returns formatted version string.

## Updating Configuration

When you need to update any information:

1. Edit the relevant section in `config.ts`
2. The changes will automatically propagate to all components using the configuration
3. No need to update individual files

## Examples

### Adding a new team member:
```typescript
export const teamConfig: TeamMember[] = [
  // existing members...
  {
    name: 'New Member',
    role: 'New Role',
    profile: 'ID-XXXX',
    github: 'https://github.com/newmember',
    linkedin: 'https://linkedin.com/in/newmember',
    email: 'newmember@domain.com'
  }
]
```

### Updating social links:
```typescript
export const socialLinks: SocialLinks = {
  github: 'https://github.com/new-repo',
  discord: 'https://discord.gg/new-server',
  // ... other links
}
```

### Adding a new navigation item:
```typescript
export const navigationMenu = [
  // existing items...
  { name: 'New Page', path: '/new-page', icon: 'NewIcon' }
]
```

This centralized approach ensures:
- Consistency across all pages
- Easy maintenance
- Single source of truth
- Type safety with TypeScript interfaces
