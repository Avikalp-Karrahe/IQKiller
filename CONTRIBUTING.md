# 🤝 Contributing to IQKiller

Thank you for your interest in contributing to IQKiller! We welcome contributions from the community and are excited to see what you'll bring to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Areas for Contribution](#areas-for-contribution)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Be patient** with newcomers
- **Focus on the issue**, not the person

## 🚀 Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm, yarn, or pnpm
- Git
- Basic knowledge of React, Next.js, and TypeScript

### Development Setup

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/iqkiller.git
   cd iqkiller
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/avikalp-karrahe/iqkiller.git
   ```

4. **Install dependencies**
   ```bash
   npm install
   ```

5. **Set up environment**
   ```bash
   cp .env.example .env.local
   # Add your API keys to .env.local
   ```

6. **Start development server**
   ```bash
   npm run dev
   ```

## 🔄 Making Changes

### Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow existing patterns
   - Add comments for complex logic

3. **Test your changes**
   ```bash
   npm run lint
   npm run build
   # Test manually in both light/dark modes
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(ui): add dark mode toggle animation
fix(api): resolve job scraping timeout issue
docs(readme): update installation instructions
```

## 🔀 Pull Request Process

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Use our PR template
   - Provide clear description
   - Link related issues
   - Add screenshots if UI changes

4. **Review Process**
   - Code review by maintainers
   - Address feedback
   - Ensure CI passes
   - Approval and merge

### Pull Request Template

```markdown
## 📝 Description
Brief description of changes

## 🔗 Related Issues
Fixes #123

## 🧪 Testing
- [ ] Tested in light mode
- [ ] Tested in dark mode
- [ ] Tested on mobile
- [ ] All API endpoints work

## 📸 Screenshots
(if applicable)

## ✅ Checklist
- [ ] Code follows project conventions
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors
```

## 💻 Coding Standards

### TypeScript

- Use strict typing
- Avoid `any` type
- Use interfaces for object types
- Export types when used across files

```typescript
// Good
interface UserProfile {
  name: string;
  email: string;
  experience: number;
}

// Avoid
const userData: any = {};
```

### React Components

- Use functional components
- Use TypeScript props interfaces
- Follow naming conventions
- Use proper file structure

```typescript
// components/ui/Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant, children, onClick }: ButtonProps) {
  return (
    <button 
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### Styling

- Use Tailwind CSS classes
- Follow mobile-first approach
- Support both light/dark themes
- Use semantic color names

```tsx
// Good
<div className="bg-white dark:bg-slate-900 p-4 rounded-lg">

// Maintain consistency
<Card className="card-gradient glass-effect">
```

### API Routes

- Use proper HTTP methods
- Handle errors gracefully
- Validate input data
- Return consistent response format

```typescript
// app/api/example/route.ts
export async function POST(request: Request) {
  try {
    const data = await request.json();
    
    // Validate input
    if (!data.field) {
      return Response.json(
        { error: 'Field is required' }, 
        { status: 400 }
      );
    }
    
    // Process data
    const result = await processData(data);
    
    return Response.json({ 
      success: true, 
      data: result 
    });
  } catch (error) {
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] **Functionality**: All features work as expected
- [ ] **Responsive**: Test on different screen sizes
- [ ] **Themes**: Verify light and dark mode
- [ ] **Performance**: No significant slowdowns
- [ ] **Accessibility**: Keyboard navigation works
- [ ] **Cross-browser**: Test in major browsers

### Testing Commands

```bash
# Lint code
npm run lint

# Type checking
npm run type-check

# Build for production
npm run build

# Start production build
npm start
```

## 🎯 Areas for Contribution

### 🌟 High Priority

- **Performance Optimization**: Bundle size, loading times
- **Accessibility**: ARIA labels, keyboard navigation
- **Mobile UX**: Touch interactions, responsive design
- **Error Handling**: Better error messages and recovery

### 🔧 Feature Additions

- **Internationalization**: Multi-language support
- **Question Categories**: Industry-specific questions
- **Export Features**: PDF/Word export of guides
- **Analytics**: Usage tracking and insights

### 🎨 UI/UX Improvements

- **Animations**: Smooth page transitions
- **Micro-interactions**: Button hover effects
- **Dark Mode**: Enhanced starry night theme
- **Components**: New reusable UI components

### 📚 Documentation

- **API Documentation**: Comprehensive API docs
- **Video Tutorials**: Getting started guides
- **Blog Posts**: Technical deep-dives
- **Examples**: Usage examples and demos

## 🆘 Need Help?

- 💬 **Discussions**: [GitHub Discussions](https://github.com/avikalp-karrahe/iqkiller/discussions)
- 🐛 **Issues**: [Report bugs](https://github.com/avikalp-karrahe/iqkiller/issues)
- 📧 **Email**: [akarrahe@ucdavis.edu](mailto:akarrahe@ucdavis.edu)

## 🏆 Recognition

Contributors will be:
- Added to our contributors list
- Mentioned in release notes
- Featured on our website (for significant contributions)

---

**Thank you for making IQKiller better! 🚀** 