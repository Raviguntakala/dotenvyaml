#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.2.0"
    exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z (e.g., 0.2.0)"
    exit 1
fi

echo "🔍 Checking git status..."
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Working directory not clean. Commit and push changes first."
    exit 1
fi

echo "✅ Working directory clean"
echo ""

echo "📝 Updating version to $VERSION..."

# Update version in all files
sed -i.bak "s/^version = .*/version = \"$VERSION\"/" pyproject.toml && rm pyproject.toml.bak
sed -i.bak "s/^version = .*/version = \"$VERSION\"/" crates/core/Cargo.toml && rm crates/core/Cargo.toml.bak
sed -i.bak "s/^version = .*/version = \"$VERSION\"/" crates/pyo3/Cargo.toml && rm crates/pyo3/Cargo.toml.bak
sed -i.bak "s/__version__ = .*/__version__ = \"$VERSION\"/" python/dotenvyaml/__init__.py && rm python/dotenvyaml/__init__.py.bak

cargo update -p dotenvyaml-core -p dotenvyaml-pyo3 --workspace

echo "✅ Version updated"
echo ""

echo "📋 Updating CHANGELOG.md..."
TODAY=$(date +%Y-%m-%d)
sed -i.bak "s/## \[Unreleased\]/## [Unreleased]\n\n## [$VERSION] - $TODAY/" CHANGELOG.md && rm CHANGELOG.md.bak
sed -i.bak "s|\[Unreleased\]:.*|[Unreleased]: https://github.com/raviguntakala/dotenvyaml/compare/v$VERSION...HEAD\n[$VERSION]: https://github.com/raviguntakala/dotenvyaml/releases/tag/v$VERSION|" CHANGELOG.md && rm CHANGELOG.md.bak

echo "✅ CHANGELOG.md updated"
echo ""

echo "🧪 Running tests..."
uv run pytest tests/ -q && cargo test -p dotenvyaml-core -q

echo "✅ Tests passed"
echo ""

echo "📦 Committing version bump..."
git add pyproject.toml crates/*/Cargo.toml Cargo.lock python/dotenvyaml/__init__.py CHANGELOG.md
git commit -m "chore: bump version to $VERSION"
git push origin main

echo "✅ Pushed version bump to main"
echo ""

echo "🏷️  Creating and pushing tag..."
git tag -a "v$VERSION" -m "v$VERSION"
git push origin "v$VERSION"

echo "✅ Tag v$VERSION pushed"
echo ""

echo "📝 Creating GitHub release..."
CHANGELOG_SECTION=$(awk "/## \[$VERSION\]/,/## \[/" CHANGELOG.md | grep -v "## \[" | sed '/^$/d' | sed '$d')

if command -v gh &> /dev/null; then
    if [[ -n "$CHANGELOG_SECTION" ]]; then
        gh release create "v$VERSION" --title "v$VERSION" --notes "$CHANGELOG_SECTION"
        echo "✅ GitHub release created"
    else
        echo "⚠️  No changelog section found for v$VERSION"
        gh release create "v$VERSION" --title "v$VERSION" --generate-notes
        echo "✅ GitHub release created with auto-generated notes"
    fi
else
    echo "⚠️  Install gh CLI: brew install gh"
fi

echo ""
echo "🎉 Release v$VERSION published!"
echo "Monitor CI: https://github.com/raviguntakala/dotenvyaml/actions"
